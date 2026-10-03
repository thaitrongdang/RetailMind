"""Stable user/item mappings and sparse interactions for one snapshot."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix


@dataclass
class Catalog:
    snapshot_id: str
    snapshot_dir: Path
    users: list[str]
    items: list[str]
    products: pd.DataFrame
    customers: pd.DataFrame
    invoice_counts: csr_matrix

    @classmethod
    def load(cls, snapshot_dir: Path) -> "Catalog":
        snapshot_dir = Path(snapshot_dir)
        manifest = json.loads((snapshot_dir / "manifest.json").read_text(encoding="utf-8"))
        products = pd.read_parquet(snapshot_dir / "products.parquet").sort_values("stock_code")
        customers = pd.read_parquet(snapshot_dir / "customers.parquet").sort_values("customer_id")
        interactions = pd.read_parquet(snapshot_dir / "interactions.parquet")
        items = products["stock_code"].astype(str).tolist()
        users = customers["customer_id"].astype(str).tolist()
        item_index = {value: index for index, value in enumerate(items)}
        user_index = {value: index for index, value in enumerate(users)}
        mapped_rows = interactions["customer_id"].map(user_index)
        mapped_columns = interactions["stock_code"].map(item_index)
        if mapped_rows.isna().any() or mapped_columns.isna().any():
            raise ValueError("Interaction mapping does not match snapshot dimensions")
        rows = mapped_rows.to_numpy(dtype=np.int32)
        columns = mapped_columns.to_numpy(dtype=np.int32)
        values = interactions["invoice_count"].to_numpy(dtype=np.float32)
        matrix = csr_matrix((values, (rows, columns)), shape=(len(users), len(items)))
        matrix.sum_duplicates()
        if matrix.nnz != len(interactions):
            raise ValueError("Duplicate customer-product interactions in snapshot")
        return cls(
            snapshot_id=manifest["snapshot_id"],
            snapshot_dir=snapshot_dir,
            users=users,
            items=items,
            products=products.reset_index(drop=True),
            customers=customers.reset_index(drop=True),
            invoice_counts=matrix,
        )

    @property
    def user_index(self) -> dict[str, int]:
        return {value: index for index, value in enumerate(self.users)}

    @property
    def item_index(self) -> dict[str, int]:
        return {value: index for index, value in enumerate(self.items)}

    @property
    def candidate_set(self) -> set[str]:
        return set(self.items)

    def seen(self, customer_id: str) -> set[str]:
        user = self.user_index.get(customer_id)
        if user is None:
            return set()
        return {self.items[index] for index in self.invoice_counts[user].indices}

    def mapping_hashes(self) -> dict[str, str]:
        return {
            "users": hashlib.sha256(json.dumps(self.users).encode()).hexdigest(),
            "items": hashlib.sha256(json.dumps(self.items).encode()).hexdigest(),
        }
