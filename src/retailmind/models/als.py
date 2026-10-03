"""CPU implicit-feedback ALS with confidence applied exactly once."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from implicit.cpu.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix
from threadpoolctl import threadpool_limits

from retailmind.models.catalog import Catalog
from retailmind.models.popularity import Popularity


class ALS:
    name = "als"

    def __init__(
        self,
        catalog: Catalog,
        factors: int = 32,
        regularization: float = 0.05,
        iterations: int = 10,
        confidence_scale: float = 20.0,
        seed: int = 42,
        model: AlternatingLeastSquares | None = None,
    ):
        self.catalog = catalog
        self.factors = factors
        self.regularization = regularization
        self.iterations = iterations
        self.confidence_scale = confidence_scale
        self.seed = seed
        self.popularity = Popularity(catalog)
        self.confidence: csr_matrix = catalog.invoice_counts.copy().astype(np.float32)
        self.confidence.data = 1.0 + confidence_scale * np.log1p(self.confidence.data)
        self.model = model

    def fit(self) -> "ALS":
        self.model = AlternatingLeastSquares(
            factors=self.factors,
            regularization=self.regularization,
            alpha=1.0,
            iterations=self.iterations,
            num_threads=4,
            random_state=self.seed,
        )
        with threadpool_limits(limits=1, user_api="blas"):
            self.model.fit(self.confidence, show_progress=False)
        if self.model.user_factors.shape[0] != len(self.catalog.users):
            raise ValueError("ALS user-factor axis does not match mapping")
        if self.model.item_factors.shape[0] != len(self.catalog.items):
            raise ValueError("ALS item-factor axis does not match mapping")
        return self

    def recommend(self, customer_id: str, k: int, with_evidence: bool = False) -> list[dict]:
        if self.model is None:
            raise RuntimeError("ALS must be fitted or loaded")
        user = self.catalog.user_index.get(customer_id)
        if user is None:
            raise KeyError(customer_id)
        n = min(k, len(self.catalog.items))
        ids, scores = self.model.recommend(
            user,
            self.confidence[user],
            N=n,
            filter_already_liked_items=False,
        )
        ranked = sorted(
            (
                (int(item), float(score))
                for item, score in zip(ids, scores)
                if np.isfinite(score)
            ),
            key=lambda pair: (-pair[1], self.catalog.items[pair[0]]),
        )
        seen = self.catalog.seen(customer_id)
        result: list[dict] = []
        user_weights = None
        for index, score in ranked:
            item = self.catalog.items[index]
            evidence = None
            if with_evidence:
                total, contributors, user_weights = self.model.explain(
                    user, self.confidence, index, user_weights=user_weights, N=3
                )
                evidence = {
                    "kind": "als_historical_contributions",
                    "explained_score": float(total),
                    "top": [
                        {
                            "historical_stock_code": self.catalog.items[int(source)],
                            "contribution": float(contribution),
                        }
                        for source, contribution in contributors
                    ],
                }
            result.append(
                {
                    "stock_code": item,
                    "score": score,
                    "source_model": self.name,
                    "repeat_item": item in seen,
                    "evidence": evidence,
                }
            )
        if len(result) < n:
            already = {row["stock_code"] for row in result}
            for fallback in self.popularity.recommend(customer_id, k=len(self.catalog.items), with_evidence=with_evidence):
                if fallback["stock_code"] in already:
                    continue
                result.append(fallback)
                if len(result) == n:
                    break
        return result

    def save(self, path: Path) -> None:
        if self.model is None:
            raise RuntimeError("ALS must be fitted before saving")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.model.save(path)

    @classmethod
    def load(
        cls,
        catalog: Catalog,
        path: Path,
        factors: int,
        regularization: float,
        iterations: int,
        confidence_scale: float,
        seed: int,
    ) -> "ALS":
        model = AlternatingLeastSquares.load(path)
        if model.user_factors.shape[0] != len(catalog.users):
            raise ValueError("Loaded ALS user mapping does not match snapshot")
        if model.item_factors.shape[0] != len(catalog.items):
            raise ValueError("Loaded ALS item mapping does not match snapshot")
        return cls(
            catalog,
            factors=factors,
            regularization=regularization,
            iterations=iterations,
            confidence_scale=confidence_scale,
            seed=seed,
            model=model,
        )
