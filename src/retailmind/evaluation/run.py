"""Offline evaluator that owns future labels outside recommendation serving."""

from __future__ import annotations

import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Protocol

import numpy as np
import pandas as pd

from retailmind.evaluation.metrics import aggregate_metrics, user_metrics
from retailmind.models.catalog import Catalog


class Recommender(Protocol):
    name: str

    def recommend(self, customer_id: str, k: int, with_evidence: bool = False) -> list[dict]:
        ...


def load_labels(processed_dir: Path, snapshot_id: str) -> dict[str, set[str]]:
    path = processed_dir / "outcomes" / snapshot_id / "labels.parquet"
    if not path.is_file():
        raise FileNotFoundError(f"Outcome artifact missing for {snapshot_id}")
    frame = pd.read_parquet(path, columns=["customer_id", "stock_code"])
    return {
        str(customer_id): set(group["stock_code"].astype(str))
        for customer_id, group in frame.groupby("customer_id", sort=False)
    }


def _history_cohort(frequency: int) -> str:
    if frequency == 1:
        return "one_invoice"
    if frequency <= 5:
        return "two_to_five_invoices"
    return "over_five_invoices"


def evaluate(
    recommender: Recommender,
    catalog: Catalog,
    processed_dir: Path,
    k: int = 10,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Score the common returning-customer cohort against full future labels."""
    labels = load_labels(processed_dir, catalog.snapshot_id)
    candidates = catalog.candidate_set
    historical = set(catalog.users)
    returning = sorted(historical & labels.keys())
    if not returning:
        raise ValueError("No historical customers returned during the label window")
    customer_rows = catalog.customers.set_index("customer_id")
    results: list[dict[str, Any]] = []
    metrics: list[dict[str, float | None]] = []
    recommendations: list[list[str]] = []
    durations: list[float] = []
    all_label_count = 0
    known_label_count = 0
    fallback_customers = 0
    cohort_metrics: dict[str, list[dict[str, float | None]]] = defaultdict(list)
    rfm_metrics: dict[str, list[dict[str, float | None]]] = defaultdict(list)
    for customer_id in returning:
        started = time.perf_counter()
        output = recommender.recommend(customer_id, k, with_evidence=False)
        durations.append((time.perf_counter() - started) * 1000)
        ranked = [str(item["stock_code"]) for item in output]
        if len(ranked) > k:
            raise ValueError("Model returned more items than requested")
        actual = labels[customer_id]
        row_metrics = user_metrics(ranked, actual, candidates, k)
        customer = customer_rows.loc[customer_id]
        cohort = _history_cohort(int(customer["frequency_invoices"]))
        rfm = str(customer["rfm_segment"])
        cohort_metrics[cohort].append(row_metrics)
        rfm_metrics[rfm].append(row_metrics)
        metrics.append(row_metrics)
        recommendations.append(ranked)
        all_label_count += len(actual)
        known_label_count += len(actual & candidates)
        used_fallback = any(item["source_model"] != recommender.name for item in output)
        fallback_customers += used_fallback
        results.append(
            {
                "customer_id": customer_id,
                "history_cohort": cohort,
                "rfm_segment": rfm,
                "labels": sorted(actual),
                "recommendations": ranked,
                "used_fallback": used_fallback,
                **row_metrics,
            }
        )
    aggregate = aggregate_metrics(metrics, recommendations, candidates)
    aggregate.update(
        {
            "model": recommender.name,
            "snapshot_id": catalog.snapshot_id,
            "k": k,
            "historical_customers": len(historical),
            "empty_label_historical_customers": len(historical) - len(returning),
            "new_future_customers": len(set(labels) - historical),
            "future_customers": len(labels),
            "candidate_products": len(candidates),
            "future_distinct_label_pairs": all_label_count,
            "known_future_label_pairs": known_label_count,
            "label_availability_micro": known_label_count / all_label_count,
            "fallback_customer_rate": fallback_customers / len(returning),
            "offline_inference_p50_ms": float(np.percentile(durations, 50)),
            "offline_inference_p95_ms": float(np.percentile(durations, 95)),
            "by_history_cohort": {
                name: aggregate_metrics(rows, [recommendations[index] for index, row in enumerate(results) if row["history_cohort"] == name], candidates)
                for name, rows in cohort_metrics.items()
            },
            "by_rfm_segment": {
                name: {
                    "customers": len(rows),
                    "recall_at_10": float(np.mean([row["recall_at_10"] for row in rows])),
                    "ndcg_at_10": float(np.mean([row["ndcg_at_10"] for row in rows])),
                }
                for name, rows in rfm_metrics.items()
            },
        }
    )
    return aggregate, results


def save_evaluation(
    aggregate: dict[str, Any], rows: list[dict[str, Any]], destination: Path
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    detail_path = destination.with_name(destination.stem + "_per_user.parquet")
    pd.DataFrame(rows).to_parquet(detail_path, index=False)
