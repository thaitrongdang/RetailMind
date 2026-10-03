"""Validation search, frozen test training, and reproducible model reports."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from retailmind.config import ProjectConfig
from retailmind.evaluation.run import evaluate
from retailmind.models.als import ALS
from retailmind.models.bundle import save_model
from retailmind.models.catalog import Catalog
from retailmind.models.itemcf import ItemCF
from retailmind.models.popularity import Popularity
from retailmind.models.routing import RoutedModel


ITEMCF_SEARCH = [
    {"neighbors": neighbors, "weighting": weighting}
    for neighbors in (20, 50)
    for weighting in ("binary", "log")
]
ALS_SEARCH = [
    {
        "factors": factors,
        "regularization": regularization,
        "iterations": 10,
        "confidence_scale": 20.0,
        "seed": 42,
    }
    for factors in (32, 64)
    for regularization in (0.05, 0.2)
]
SIMPLICITY_ORDER = {"popularity": 0, "itemcf": 1, "als": 2}


def _catalog(config: ProjectConfig, name: str) -> Catalog:
    summary = json.loads((config.reports_dir / "snapshots.json").read_text(encoding="utf-8"))
    snapshot_id = summary[name]["snapshot_id"]
    return Catalog.load(config.processed_dir / "snapshots" / snapshot_id)


def _model(name: str, catalog: Catalog, params: dict[str, Any]) -> Popularity | ItemCF | ALS:
    if name == "popularity":
        return Popularity(catalog)
    if name == "itemcf":
        return ItemCF(catalog, **params).fit()
    if name == "als":
        return ALS(catalog, **params).fit()
    raise ValueError(f"Unknown model: {name}")


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _save_per_user(config: ProjectConfig, name: str, rows: list[dict[str, Any]]) -> None:
    path = config.processed_dir / "evaluations" / f"{name}_selected_per_user.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(path, index=False)


def train_validation(config: ProjectConfig) -> dict[str, Any]:
    """Choose model, parameters, and routing using validation only."""
    catalog = _catalog(config, "validation")
    search = {
        "popularity": [{"history_days": 90}],
        "itemcf": ITEMCF_SEARCH,
        "als": ALS_SEARCH,
    }
    experiments: list[dict[str, Any]] = []
    best: dict[str, tuple[Popularity | ItemCF | ALS, dict[str, Any], dict[str, Any]]] = {}
    for name, parameter_sets in search.items():
        for params in parameter_sets:
            print(f"Fitting validation {name} {params}", flush=True)
            model = _model(name, catalog, params if name != "popularity" else {})
            aggregate, _ = evaluate(model, catalog, config.processed_dir, config.k)
            experiments.append({"model": name, "params": params, "metrics": aggregate})
            previous = best.get(name)
            if previous is None or aggregate["ndcg_at_10"] > previous[2]["ndcg_at_10"]:
                best[name] = (model, params, aggregate)
            print(
                f"  NDCG@10={aggregate['ndcg_at_10']:.6f} "
                f"Recall@10={aggregate['recall_at_10']:.6f}",
                flush=True,
            )
    highest = max(result[2]["ndcg_at_10"] for result in best.values())
    candidates = [
        name for name, result in best.items()
        if highest - result[2]["ndcg_at_10"] <= 0.005
    ]
    selected_name = min(candidates, key=lambda name: SIMPLICITY_ORDER[name])
    selected_model = best[selected_name][0]
    routing: list[dict[str, Any]] = []
    best_route: tuple[int, dict[str, Any], list[dict[str, Any]]] | None = None
    for min_invoices in (1, 2, 3):
        routed = RoutedModel(catalog, selected_model, min_invoices=min_invoices)
        aggregate, rows = evaluate(routed, catalog, config.processed_dir, config.k)
        routing.append({"min_invoices": min_invoices, "metrics": aggregate})
        if best_route is None or aggregate["ndcg_at_10"] > best_route[1]["ndcg_at_10"]:
            best_route = (min_invoices, aggregate, rows)
    assert best_route is not None
    for name, (model, params, _) in best.items():
        save_model(model, catalog, config.root / "artifacts", params)
    selection = {
        "selected_model": selected_name,
        "selected_params": best[selected_name][1],
        "min_invoices": best_route[0],
        "selection_metric": "ndcg_at_10_validation",
        "simplicity_tolerance_absolute": 0.005,
        "validation_snapshot_id": catalog.snapshot_id,
        "source_hash": json.loads(
            (catalog.snapshot_dir / "manifest.json").read_text(encoding="utf-8")
        )["source_hash"],
        "evaluation_contract": {
            "horizon_days": config.horizon_days,
            "k": config.k,
            "excluded_stock_codes": sorted(config.excluded_stock_codes),
            "repeat_purchases_allowed": True,
        },
        "model_params": {name: result[1] for name, result in best.items()},
        "best_model_metrics": {name: result[2] for name, result in best.items()},
        "selected_routed_metrics": best_route[1],
        "routing_experiments": routing,
        "experiments": experiments,
        "frozen_before_test": True,
    }
    _write_json(config.reports_dir / "validation_selection.json", selection)
    _save_per_user(config, "validation", best_route[2])
    print(
        f"Selected {selected_name} {best[selected_name][1]}, "
        f"min_invoices={best_route[0]}, NDCG@10={best_route[1]['ndcg_at_10']:.6f}",
        flush=True,
    )
    return selection


def train_test(config: ProjectConfig) -> dict[str, Any]:
    """Train at test cutoff using frozen validation choices; evaluate once."""
    selection_path = config.reports_dir / "validation_selection.json"
    if not selection_path.is_file():
        raise FileNotFoundError("Freeze validation selection before evaluating test")
    report_path = config.reports_dir / "test_metrics.json"
    if report_path.exists():
        raise FileExistsError(
            "Final test report already exists; document a protocol correction before rerun"
        )
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    if not selection.get("frozen_before_test"):
        raise ValueError("Validation configuration is not frozen")
    catalog = _catalog(config, "test")
    snapshot_manifest = json.loads(
        (catalog.snapshot_dir / "manifest.json").read_text(encoding="utf-8")
    )
    if snapshot_manifest["source_hash"] != selection["source_hash"]:
        raise ValueError("Test source hash differs from validation source")
    policy = snapshot_manifest["policy"]
    contract = selection["evaluation_contract"]
    if (
        policy["horizon_days"] != contract["horizon_days"]
        or sorted(policy["excluded_stock_codes"]) != contract["excluded_stock_codes"]
        or policy["repeat_purchases_allowed"] != contract["repeat_purchases_allowed"]
        or config.k != contract["k"]
    ):
        raise ValueError("Test evaluation contract differs from frozen validation")
    trained: dict[str, Popularity | ItemCF | ALS] = {}
    evaluated: dict[str, dict[str, Any]] = {}
    for name, params in selection["model_params"].items():
        print(f"Fitting frozen test {name} {params}", flush=True)
        model = _model(name, catalog, params if name != "popularity" else {})
        trained[name] = model
        aggregate, _ = evaluate(model, catalog, config.processed_dir, config.k)
        evaluated[name] = aggregate
        save_model(model, catalog, config.root / "artifacts", params)
    routed = RoutedModel(
        catalog,
        trained[selection["selected_model"]],
        min_invoices=selection["min_invoices"],
    )
    selected_metrics, per_user = evaluate(routed, catalog, config.processed_dir, config.k)
    report = {
        "test_snapshot_id": catalog.snapshot_id,
        "validation_snapshot_id": selection["validation_snapshot_id"],
        "source_hash": selection["source_hash"],
        "selected_model": selection["selected_model"],
        "selected_params": selection["selected_params"],
        "min_invoices": selection["min_invoices"],
        "model_metrics": evaluated,
        "selected_routed_metrics": selected_metrics,
        "evaluated_at_local_time": datetime.now().isoformat(timespec="seconds"),
        "note": "Configuration was frozen in validation_selection.json before test evaluation.",
    }
    _write_json(report_path, report)
    _save_per_user(config, "test", per_user)
    print(
        f"Final test {selection['selected_model']} "
        f"NDCG@10={selected_metrics['ndcg_at_10']:.6f} "
        f"Recall@10={selected_metrics['recall_at_10']:.6f}",
        flush=True,
    )
    return report
