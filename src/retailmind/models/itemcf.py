"""Sparse item-item cosine similarity with self-similarity removed."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix, load_npz, save_npz

from retailmind.models.catalog import Catalog
from retailmind.models.popularity import Popularity


class ItemCF:
    name = "itemcf"

    def __init__(
        self,
        catalog: Catalog,
        neighbors: int = 50,
        weighting: str = "binary",
        similarity: csr_matrix | None = None,
    ):
        if weighting not in {"binary", "log"}:
            raise ValueError("ItemCF weighting must be binary or log")
        self.catalog = catalog
        self.neighbors = neighbors
        self.weighting = weighting
        self.popularity = Popularity(catalog)
        self.user_items = catalog.invoice_counts.copy().astype(np.float32)
        self.user_items.data = (
            np.ones_like(self.user_items.data)
            if weighting == "binary"
            else np.log1p(self.user_items.data)
        )
        self.similarity = similarity

    def fit(self) -> "ItemCF":
        matrix = self.user_items
        cooccurrence = (matrix.T @ matrix).tocsr()
        norms = np.sqrt(np.asarray(matrix.power(2).sum(axis=0)).ravel())
        rows: list[int] = []
        columns: list[int] = []
        values: list[float] = []
        for source in range(matrix.shape[1]):
            start, end = cooccurrence.indptr[source : source + 2]
            targets = cooccurrence.indices[start:end]
            co_values = cooccurrence.data[start:end]
            denominator = norms[source] * norms[targets]
            valid = (targets != source) & (denominator > 0)
            pairs = [
                (int(target), float(value / norm))
                for target, value, norm in zip(targets[valid], co_values[valid], denominator[valid])
            ]
            pairs.sort(key=lambda pair: (-pair[1], self.catalog.items[pair[0]]))
            for target, score in pairs[: self.neighbors]:
                rows.append(source)
                columns.append(target)
                values.append(score)
        self.similarity = csr_matrix(
            (np.asarray(values, dtype=np.float32), (rows, columns)),
            shape=(len(self.catalog.items), len(self.catalog.items)),
        )
        if self.similarity.diagonal().any():
            raise ValueError("ItemCF self-similarity was not removed")
        return self

    def recommend(self, customer_id: str, k: int, with_evidence: bool = False) -> list[dict]:
        if self.similarity is None:
            raise RuntimeError("ItemCF must be fitted or loaded")
        user = self.catalog.user_index.get(customer_id)
        if user is None:
            raise KeyError(customer_id)
        raw_scores = (self.user_items[user] @ self.similarity).toarray().ravel()
        ordered = sorted(
            (index for index, score in enumerate(raw_scores) if np.isfinite(score) and score > 0),
            key=lambda index: (-float(raw_scores[index]), self.catalog.items[index]),
        )
        seen = self.catalog.seen(customer_id)
        result: list[dict] = []
        for index in ordered[:k]:
            item = self.catalog.items[index]
            result.append(
                {
                    "stock_code": item,
                    "score": float(raw_scores[index]),
                    "source_model": self.name,
                    "repeat_item": item in seen,
                    "evidence": self._evidence(user, index) if with_evidence else None,
                }
            )
        if len(result) < k:
            already = {row["stock_code"] for row in result}
            for fallback in self.popularity.recommend(customer_id, k=len(self.catalog.items), with_evidence=with_evidence):
                if fallback["stock_code"] in already:
                    continue
                result.append(fallback)
                if len(result) == k:
                    break
        return result

    def _evidence(self, user: int, target: int) -> dict:
        row = self.user_items[user]
        contributions = [
            {
                "historical_stock_code": self.catalog.items[source],
                "contribution": float(weight * self.similarity[source, target]),
            }
            for source, weight in zip(row.indices, row.data)
            if self.similarity[source, target] > 0
        ]
        contributions.sort(key=lambda part: (-part["contribution"], part["historical_stock_code"]))
        return {"kind": "item_similarity_contributions", "top": contributions[:3]}

    def save(self, path: Path) -> None:
        if self.similarity is None:
            raise RuntimeError("ItemCF must be fitted before saving")
        path.parent.mkdir(parents=True, exist_ok=True)
        save_npz(path, self.similarity)

    @classmethod
    def load(cls, catalog: Catalog, path: Path, neighbors: int, weighting: str) -> "ItemCF":
        matrix = load_npz(path).tocsr()
        if matrix.shape != (len(catalog.items), len(catalog.items)):
            raise ValueError("ItemCF mapping shape does not match snapshot")
        return cls(catalog, neighbors=neighbors, weighting=weighting, similarity=matrix)
