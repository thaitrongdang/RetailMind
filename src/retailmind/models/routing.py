"""Validation-selected fallback for customers with too little history."""

from __future__ import annotations

from retailmind.models.als import ALS
from retailmind.models.catalog import Catalog
from retailmind.models.itemcf import ItemCF
from retailmind.models.popularity import Popularity


class RoutedModel:
    def __init__(
        self,
        catalog: Catalog,
        primary: Popularity | ItemCF | ALS,
        min_invoices: int = 1,
    ):
        self.catalog = catalog
        self.primary = primary
        self.popularity = Popularity(catalog)
        self.min_invoices = min_invoices
        self.name = primary.name
        self.frequency = {
            str(customer_id): int(frequency)
            for customer_id, frequency in zip(
                catalog.customers["customer_id"], catalog.customers["frequency_invoices"]
            )
        }

    def recommend(self, customer_id: str, k: int, with_evidence: bool = False) -> list[dict]:
        if customer_id not in self.frequency:
            raise KeyError(customer_id)
        if self.frequency[customer_id] < self.min_invoices:
            return self.popularity.recommend(customer_id, k, with_evidence=with_evidence)
        return self.primary.recommend(customer_id, k, with_evidence=with_evidence)
