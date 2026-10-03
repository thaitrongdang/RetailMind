"""Distinct-customer popularity from the 90 days before a cutoff."""

from __future__ import annotations

from retailmind.models.catalog import Catalog


class Popularity:
    name = "popularity"

    def __init__(self, catalog: Catalog):
        self.catalog = catalog
        products = catalog.products
        self.counts = {
            str(code): int(count)
            for code, count in zip(products["stock_code"], products["popularity_90d"])
        }
        self.ranked = sorted(catalog.items, key=lambda item: (-self.counts[item], item))

    def recommend(self, customer_id: str | None, k: int, with_evidence: bool = False) -> list[dict]:
        if customer_id is not None and customer_id not in self.catalog.user_index:
            raise KeyError(customer_id)
        seen = self.catalog.seen(customer_id) if customer_id else set()
        return [
            {
                "stock_code": item,
                "score": float(self.counts[item]),
                "source_model": self.name,
                "repeat_item": item in seen,
                "evidence": (
                    {"kind": "distinct_customers_90d", "count": self.counts[item]}
                    if with_evidence
                    else None
                ),
            }
            for item in self.ranked[:k]
        ]
