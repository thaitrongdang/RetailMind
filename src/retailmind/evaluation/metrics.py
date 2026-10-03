"""Binary ranking metrics with explicit empty-label and candidate policies."""

from __future__ import annotations

from math import log2
from statistics import mean
from typing import Any


def user_metrics(
    ranked_items: list[str],
    labels: set[str],
    candidates: set[str],
    k: int = 10,
) -> dict[str, float | None]:
    """Evaluate one returning customer; labels may include future-only items."""
    if not labels:
        raise ValueError("Empty-label customers are counted, not scored")
    top = ranked_items[:k]
    if len(top) != len(set(top)):
        raise ValueError("Recommendation list has duplicate products")
    if not set(top).issubset(candidates):
        raise ValueError("Recommendation list contains an ineligible product")
    hits = [item in labels for item in top]
    dcg = sum(1.0 / log2(rank + 2) for rank, hit in enumerate(hits) if hit)
    idcg = sum(1.0 / log2(rank + 2) for rank in range(min(len(labels), k)))
    eligible = labels & candidates
    return {
        "recall_at_10": sum(hits) / len(labels),
        "ndcg_at_10": dcg / idcg,
        "hit_rate_at_10": float(any(hits)),
        "eligible_recall_at_10": (sum(hits) / len(eligible)) if eligible else None,
        "label_availability": len(eligible) / len(labels),
    }


def aggregate_metrics(
    per_user: list[dict[str, float | None]],
    recommendations: list[list[str]],
    candidates: set[str],
) -> dict[str, Any]:
    """Macro-average user metrics and report catalog coverage."""
    if not per_user:
        raise ValueError("No returning historical customers to evaluate")
    fields = ("recall_at_10", "ndcg_at_10", "hit_rate_at_10", "eligible_recall_at_10")
    result = {
        key: mean(float(row[key]) for row in per_user if row[key] is not None)
        if any(row[key] is not None for row in per_user)
        else None
        for key in fields
    }
    result["label_availability_macro"] = mean(
        float(row["label_availability"]) for row in per_user
    )
    result["catalog_coverage"] = (
        len({item for ranked in recommendations for item in ranked} & candidates)
        / len(candidates)
        if candidates
        else 0.0
    )
    result["evaluated_customers"] = len(per_user)
    result["eligible_label_customers"] = sum(
        row["eligible_recall_at_10"] is not None for row in per_user
    )
    return result
