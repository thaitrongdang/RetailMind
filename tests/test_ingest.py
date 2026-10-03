"""Fixture checks for lineage, cleaning reasons, and repeatable ingestion."""

from datetime import datetime
from pathlib import Path

import pyarrow.parquet as pq
from openpyxl import Workbook

from retailmind.config import ProjectConfig
from retailmind.data.ingest import prepare_workbook


HEADER = ("Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "Customer ID", "Country")


def _config(tmp_path: Path) -> ProjectConfig:
    workbook_path = tmp_path / "source.xlsx"
    workbook = Workbook()
    first = workbook.active
    first.title = "First year"
    first.append(HEADER)
    first.append((1001, "SKU-A", "Widget A", 2, datetime(2011, 8, 1), 3.5, 1.0, "UK"))
    first.append((1001, "SKU-B", "Widget B", 1, datetime(2011, 8, 1), 5, 1.0, "UK"))
    first.append(("C1002", "SKU-A", "Widget A", -1, datetime(2011, 8, 2), 3.5, 1.0, "UK"))
    first.append((1003, "SKU-A", "Widget A", 1, datetime(2011, 8, 3), 3.5, None, "UK"))
    second = workbook.create_sheet("Second year")
    second.append(HEADER)
    second.append((1004, "SKU-A", "Widget A", 1, "bad date", 3.5, 2, "UK"))
    second.append((1005, "SKU-A", "Widget A", 1, datetime(2011, 8, 4), 0, 2, "UK"))
    second.append((1006, None, "Missing code", 1, datetime(2011, 8, 5), 3, 2, "UK"))
    second.append((1001, "SKU-A", "Widget A", 2, datetime(2011, 8, 1), 3.5, 1.0, "UK"))
    workbook.save(workbook_path)
    return ProjectConfig(
        root=tmp_path,
        workbook=workbook_path,
        processed_dir=tmp_path / "processed",
        reports_dir=tmp_path / "reports",
        excluded_stock_codes=frozenset(),
        horizon_days=30,
        k=10,
        validation_cutoff=datetime(2011, 9, 1),
        test_cutoff=datetime(2011, 11, 1),
    )


def test_ingest_reconciles_reasons_and_preserves_lineage(tmp_path: Path) -> None:
    config = _config(tmp_path)
    result = prepare_workbook(config)
    quality = result["quality"]
    assert result["manifest"]["total_rows"] == 8
    assert quality["reconciled"]
    assert quality["reason_counts"] == {
        "cancellation": 1,
        "invalid_date": 1,
        "missing_stock_code": 1,
        "nonpositive_price": 1,
        "sale_anonymous": 1,
        "sale_identified": 3,
    }
    assert quality["suspicious_duplicate_extra_rows"] == 1
    raw = pq.read_table(config.processed_dir / "raw_transactions.parquet").to_pydict()
    assert len(set(raw["raw_row_id"])) == 8
    assert raw["source_row"][:4] == [2, 3, 4, 5]
    classified = pq.read_table(config.processed_dir / "transactions.parquet").to_pandas()
    assert classified.loc[classified["reason_code"] == "sale_identified", "customer_id"].eq("1").all()
    assert classified.loc[classified["reason_code"] == "sale_anonymous", "customer_id"].isna().all()


def test_prepare_same_source_is_idempotent(tmp_path: Path) -> None:
    config = _config(tmp_path)
    first = prepare_workbook(config)
    manifest_before = (config.reports_dir / "data_manifest.json").read_bytes()
    quality_before = (config.reports_dir / "data_quality.json").read_bytes()
    second = prepare_workbook(config)
    assert first == second
    assert manifest_before == (config.reports_dir / "data_manifest.json").read_bytes()
    assert quality_before == (config.reports_dir / "data_quality.json").read_bytes()
    assert pq.read_metadata(config.processed_dir / "raw_transactions.parquet").num_rows == 8
