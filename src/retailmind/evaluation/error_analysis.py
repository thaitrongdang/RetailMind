"""Deterministic error analysis from frozen offline predictions."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

import pandas as pd

from retailmind.config import ProjectConfig
from retailmind.models.catalog import Catalog


def analyze_errors(config: ProjectConfig, snapshot_name: str = "test") -> dict[str, Any]:
    report = json.loads(
        (config.reports_dir / f"{snapshot_name}_metrics.json").read_text(encoding="utf-8")
    )
    snapshot_id = report[f"{snapshot_name}_snapshot_id"]
    catalog = Catalog.load(config.processed_dir / "snapshots" / snapshot_id)
    details = pd.read_parquet(
        config.processed_dir / "evaluations" / f"{snapshot_name}_selected_per_user.parquet"
    )
    candidates = catalog.candidate_set
    no_hit_by_cohort: dict[str, Counter] = defaultdict(Counter)
    examples: dict[str, dict[str, Any]] = {}
    repeat_pairs = 0
    unknown_pairs = 0
    total_pairs = 0
    zero_hit = 0
    for row in details.sort_values("customer_id").to_dict("records"):
        customer_id = str(row["customer_id"])
        labels = set(row["labels"])
        ranked = list(row["recommendations"])
        seen = catalog.seen(customer_id)
        hits = labels & set(ranked)
        cohort = str(row["history_cohort"])
        no_hit_by_cohort[cohort]["customers"] += 1
        if not hits:
            zero_hit += 1
            no_hit_by_cohort[cohort]["zero_hit"] += 1
            examples.setdefault(
                f"zero_hit_{cohort}",
                {
                    "customer_id": customer_id,
                    "history_cohort": cohort,
                    "labels": sorted(labels),
                    "recommendations": ranked,
                    "repeat_labels": sorted(labels & seen),
                    "future_only_labels": sorted(labels - candidates),
                },
            )
        if labels - candidates:
            examples.setdefault(
                "future_only_label",
                {
                    "customer_id": customer_id,
                    "history_cohort": cohort,
                    "labels": sorted(labels),
                    "recommendations": ranked,
                    "future_only_labels": sorted(labels - candidates),
                },
            )
        repeat_pairs += len(labels & seen)
        unknown_pairs += len(labels - candidates)
        total_pairs += len(labels)
    result = {
        "snapshot_id": snapshot_id,
        "selected_model": report["selected_model"],
        "evaluated_customers": len(details),
        "zero_hit_customers": zero_hit,
        "zero_hit_rate": zero_hit / len(details),
        "future_label_pairs": total_pairs,
        "repeat_label_pairs": repeat_pairs,
        "repeat_label_pair_rate": repeat_pairs / total_pairs,
        "future_only_label_pairs": unknown_pairs,
        "future_only_label_pair_rate": unknown_pairs / total_pairs,
        "zero_hit_by_history_cohort": {
            name: {
                "customers": values["customers"],
                "zero_hit": values["zero_hit"],
                "zero_hit_rate": values["zero_hit"] / values["customers"],
            }
            for name, values in sorted(no_hit_by_cohort.items())
        },
        "examples": examples,
        "interpretation_limit": (
            "A miss is an offline mismatch with observed purchases, not evidence that "
            "a customer disliked the recommendation or saw every candidate product."
        ),
    }
    output = config.reports_dir / f"{snapshot_name}_error_analysis.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result
