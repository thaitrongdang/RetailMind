"""Cutoff boundary and future-invariance checks for snapshot artifacts."""

import json
from datetime import datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from retailmind.config import ProjectConfig
from retailmind.data.snapshots import build_snapshot


def _row(number: int, invoice: str, customer: str | None, product: str, when: str, reason: str) -> dict:
    return {
        "raw_row_id": f"fixture:{number}",
        "invoice_no": invoice,
        "stock_code": product,
        "description": f"Product {product}",
        "quantity": 1,
        "invoice_date": datetime.fromisoformat(when),
        "unit_price": 2.0,
        "customer_id": customer,
        "country": "UK",
        "line_value": 2.0,
        "reason_code": reason,
    }


def _config(tmp_path: Path, future_product: str = "SKU-C") -> ProjectConfig:
    processed = tmp_path / "processed"
    reports = tmp_path / "reports"
    processed.mkdir(parents=True)
    reports.mkdir(parents=True)
    rows = [
        _row(1, "A100", "C1", "SKU-A", "2011-08-31T23:59:00", "sale_identified"),
        _row(2, "A100", "C1", "SKU-B", "2011-08-31T23:59:00", "sale_identified"),
        _row(3, "A101", None, "SKU-Z", "2011-08-31T23:59:00", "sale_anonymous"),
        _row(4, "A102", "C1", "SKU-B", "2011-09-01T00:00:00", "sale_identified"),
        _row(5, "A103", "C2", future_product, "2011-09-05T12:00:00", "sale_identified"),
        _row(6, "A104", "C1", "SKU-E", "2011-10-01T00:00:00", "sale_identified"),
        _row(7, "A105", "C1", "SKU-D", "2011-10-02T00:00:00", "sale_identified"),
    ]
    pq.write_table(pa.Table.from_pylist(rows), processed / "transactions.parquet")
    (reports / "data_manifest.json").write_text(
        json.dumps({"workbook_sha256": "f" * 64}), encoding="utf-8"
    )
    return ProjectConfig(
        root=tmp_path,
        workbook=tmp_path / "unused.xlsx",
        processed_dir=processed,
        reports_dir=reports,
        excluded_stock_codes=frozenset(),
        horizon_days=30,
        k=10,
        validation_cutoff=datetime(2011, 9, 1),
        test_cutoff=datetime(2011, 11, 1),
    )


def test_cutoff_and_outcome_boundaries(tmp_path: Path) -> None:
    config = _config(tmp_path)
    manifest = build_snapshot(config, "validation")
    snapshot = config.processed_dir / "snapshots" / manifest["snapshot_id"]
    outcomes = config.processed_dir / "outcomes" / manifest["snapshot_id"]
    products = pq.read_table(snapshot / "products.parquet").to_pydict()
    customers = pq.read_table(snapshot / "customers.parquet").to_pydict()
    labels = pq.read_table(outcomes / "labels.parquet").to_pydict()
    assert set(products["stock_code"]) == {"SKU-A", "SKU-B"}
    assert customers["customer_id"] == ["C1"]
    assert set(zip(labels["customer_id"], labels["stock_code"])) == {
        ("C1", "SKU-B"),
        ("C2", "SKU-C"),
    }
    assert manifest["counts"]["history_identified_lines"] == 2
    assert manifest["counts"]["history_analytics_lines"] == 3


def test_future_change_leaves_service_artifacts_unchanged(tmp_path: Path) -> None:
    first = _config(tmp_path / "first", "SKU-C")
    second = _config(tmp_path / "second", "SKU-X")
    first_manifest = build_snapshot(first, "validation")
    second_manifest = build_snapshot(second, "validation")
    for filename in ("interactions.parquet", "customers.parquet", "products.parquet"):
        first_table = pq.read_table(
            first.processed_dir / "snapshots" / first_manifest["snapshot_id"] / filename
        )
        second_table = pq.read_table(
            second.processed_dir / "snapshots" / second_manifest["snapshot_id"] / filename
        )
        assert first_table.equals(second_table)
