"""Read-only, cutoff-bound recommendation service. Future labels are never loaded here."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import pandas as pd

from retailmind.config import ProjectConfig
from retailmind.models.bundle import load_model
from retailmind.models.catalog import Catalog


class ServiceUnavailable(Exception):
    """A required snapshot or model artifact is absent or invalid."""


@dataclass
class SnapshotService:
    name: str
    manifest: dict[str, Any]
    catalog: Catalog
    models: dict[str, Any]
    metadata: dict[str, dict[str, Any]]
    selected_model: str
    min_invoices: int

    @property
    def snapshot_id(self) -> str:
        return self.manifest["snapshot_id"]

    def recommend(self, customer_id: str | None, k: int, model_name: str = "selected") -> dict[str, Any]:
        if customer_id is not None and customer_id not in self.catalog.user_index:
            raise KeyError(customer_id)
        requested_model = self.selected_model if model_name == "selected" else model_name
        if requested_model not in ("itemcf", "als", "popularity"):
            raise ValueError("Unknown model")
        if customer_id is None:
            actual_model = "popularity"
            reason = "explicit_new_customer"
            mode = "new_customer"
        elif requested_model != "popularity" and self._invoice_count(customer_id) < self.min_invoices:
            actual_model = "popularity"
            reason = "insufficient_history"
            mode = "fallback"
        else:
            actual_model = requested_model
            reason = "selected_or_requested_model"
            mode = "historical_customer"
        if actual_model not in self.models:
            raise ServiceUnavailable(f"Model bundle unavailable: {actual_model}")
        rows = self.models[actual_model].recommend(customer_id, k, with_evidence=True)
        descriptions = dict(zip(self.catalog.products.stock_code, self.catalog.products.description))
        items = [
            {
                "rank": rank,
                "stock_code": row["stock_code"],
                "score": float(row["score"]),
                "description_as_of_cutoff": descriptions.get(row["stock_code"], row["stock_code"]),
                "repeat_item": bool(row["repeat_item"]),
                "source_model": row["source_model"],
                "evidence": row["evidence"],
            }
            for rank, row in enumerate(rows, 1)
        ]
        return {
            "snapshot_id": self.snapshot_id,
            "train_cutoff": self.manifest["cutoff"],
            "model_name": actual_model,
            "model_version": self.metadata[actual_model]["model_version"],
            "requested_model": model_name,
            "customer_id": customer_id,
            "k_requested": k,
            "k_returned": len(items),
            "mode": mode,
            "reason_code": reason,
            "score_semantics": "ranking_score_not_purchase_probability",
            "items": items,
        }

    def _invoice_count(self, customer_id: str) -> int:
        row = self.catalog.customers.loc[self.catalog.customers.customer_id == customer_id]
        return int(row.iloc[0].frequency_invoices)

    def customer(self, customer_id: str, history_limit: int = 25) -> dict[str, Any]:
        row = self.catalog.customers.loc[self.catalog.customers.customer_id == customer_id]
        if row.empty:
            raise KeyError(customer_id)
        profile = json.loads(row.to_json(orient="records", date_format="iso"))[0]
        history = pd.read_parquet(
            self.catalog.snapshot_dir / "analytics_sales.parquet",
            filters=[("customer_id", "==", customer_id)],
        )
        history = history.sort_values("invoice_date", ascending=False).head(history_limit)
        return {
            "snapshot_id": self.snapshot_id,
            "train_cutoff": self.manifest["cutoff"],
            "profile": profile,
            "recent_lines": json.loads(history.to_json(orient="records", date_format="iso")),
        }

    def products(self, q: str | None, limit: int) -> dict[str, Any]:
        products = self.catalog.products
        if q:
            mask = products.stock_code.str.contains(q, case=False, regex=False) | products.description.str.contains(q, case=False, regex=False, na=False)
            products = products.loc[mask]
        products = products.sort_values(["popularity_90d", "stock_code"], ascending=[False, True])
        return {"snapshot_id": self.snapshot_id, "train_cutoff": self.manifest["cutoff"], "items": json.loads(products.head(limit).to_json(orient="records", date_format="iso")), "total_matches": len(products)}

    def similar(self, stock_code: str, k: int) -> dict[str, Any]:
        index = self.catalog.item_index.get(stock_code)
        if index is None:
            raise KeyError(stock_code)
        model = self.models.get("itemcf")
        if model is None:
            raise ServiceUnavailable("ItemCF bundle unavailable")
        vector = model.similarity.getrow(index)
        pairs = sorted(
            ((int(item), float(score)) for item, score in zip(vector.indices, vector.data) if item != index),
            key=lambda pair: (-pair[1], self.catalog.items[pair[0]]),
        )[:k]
        descriptions = dict(zip(self.catalog.products.stock_code, self.catalog.products.description))
        return {
            "snapshot_id": self.snapshot_id,
            "train_cutoff": self.manifest["cutoff"],
            "stock_code": stock_code,
            "model_name": "itemcf",
            "model_version": self.metadata["itemcf"]["model_version"],
            "items": [
                {"rank": rank, "stock_code": self.catalog.items[item], "score": score,
                 "description_as_of_cutoff": descriptions.get(self.catalog.items[item], self.catalog.items[item])}
                for rank, (item, score) in enumerate(pairs, 1)
            ],
        }


def load_services(config: ProjectConfig) -> tuple[dict[str, SnapshotService], dict[str, str]]:
    selection_path = config.reports_dir / "validation_selection.json"
    if not selection_path.is_file():
        return {}, {"global": "validation selection report missing"}
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    summary_path = config.reports_dir / "snapshots.json"
    if not summary_path.is_file():
        return {}, {"global": "snapshot summary missing"}
    summaries = json.loads(summary_path.read_text(encoding="utf-8"))
    services: dict[str, SnapshotService] = {}
    errors: dict[str, str] = {}
    for name, summary in summaries.items():
        directory = config.processed_dir / "snapshots" / summary["snapshot_id"]
        try:
            manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
            catalog = Catalog.load(directory)
            if manifest["snapshot_id"] != summary["snapshot_id"]:
                raise ValueError("Snapshot manifest mismatch")
            models: dict[str, Any] = {}
            metadata: dict[str, dict[str, Any]] = {}
            for model_name in ("popularity", "itemcf", "als"):
                try:
                    models[model_name], metadata[model_name] = load_model(
                        catalog, config.root / "artifacts", model_name
                    )
                except (FileNotFoundError, ValueError, KeyError) as exc:
                    errors[f"{name}:{model_name}"] = type(exc).__name__
            if "popularity" not in models:
                # Popularity is deterministic from the cutoff catalog; still report a missing bundle.
                errors[name] = "popularity bundle missing"
                continue
            services[name] = SnapshotService(
                name, manifest, catalog, models, metadata,
                selection["selected_model"], int(selection["min_invoices"]),
            )
        except (FileNotFoundError, ValueError, KeyError) as exc:
            errors[name] = type(exc).__name__
    return services, errors