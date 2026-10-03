"""Build cutoff-safe customer, product, interaction, and outcome artifacts."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import timedelta
from pathlib import Path
from typing import Any

import duckdb

from retailmind.config import ProjectConfig


SNAPSHOT_VERSION = "v1-2026-10-03"


def _quoted_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").replace("'", "''")


def _copy_query(connection: duckdb.DuckDBPyConnection, query: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".parquet.tmp")
    connection.execute(
        f"COPY ({query}) TO '{_quoted_path(temporary)}' (FORMAT PARQUET, COMPRESSION ZSTD)"
    )
    os.replace(temporary, destination)


def _source_manifest(config: ProjectConfig) -> dict[str, Any]:
    path = config.reports_dir / "data_manifest.json"
    if not path.is_file():
        raise FileNotFoundError("Run 'retailmind prepare' before building snapshots")
    return json.loads(path.read_text(encoding="utf-8"))


def build_snapshot(config: ProjectConfig, name: str) -> dict[str, Any]:
    """Build one immutable-by-ID snapshot and its separate future labels."""
    cutoff = config.cutoff(name)
    outcome_end = cutoff + timedelta(days=config.horizon_days)
    source = _source_manifest(config)
    source_hash = source["workbook_sha256"]
    policy = {
        "snapshot_version": SNAPSHOT_VERSION,
        "cutoff": cutoff.isoformat(),
        "horizon_days": config.horizon_days,
        "excluded_stock_codes": sorted(config.excluded_stock_codes),
        "source_hash": source_hash,
        "repeat_purchases_allowed": True,
    }
    policy_hash = hashlib.sha256(json.dumps(policy, sort_keys=True).encode()).hexdigest()[:12]
    snapshot_id = f"{name}-{cutoff:%Y%m%d}-{source_hash[:12]}-{policy_hash}"
    snapshot_dir = config.processed_dir / "snapshots" / snapshot_id
    outcome_dir = config.processed_dir / "outcomes" / snapshot_id
    transactions = config.processed_dir / "transactions.parquet"
    if not transactions.is_file():
        raise FileNotFoundError("Classified transactions not found; run 'retailmind prepare'")
    connection = duckdb.connect()
    try:
        connection.execute(
            f"CREATE VIEW transactions AS SELECT * FROM read_parquet('{_quoted_path(transactions)}')"
        )
        observed_max = connection.execute(
            "SELECT MAX(invoice_date) FROM transactions"
        ).fetchone()[0]
        if observed_max is None or observed_max < outcome_end:
            raise ValueError(
                f"Outcome window through {outcome_end} is not fully observed; "
                f"maximum timestamp is {observed_max}"
            )
        cutoff_sql = cutoff.isoformat(sep=" ")
        end_sql = outcome_end.isoformat(sep=" ")
        connection.execute(
            f"""
            CREATE VIEW history_sales AS
            SELECT * FROM transactions
            WHERE reason_code = 'sale_identified'
              AND invoice_date < TIMESTAMP '{cutoff_sql}'
            """
        )
        connection.execute(
            f"""
            CREATE VIEW analytics_sales AS
            SELECT * FROM transactions
            WHERE reason_code IN ('sale_identified', 'sale_anonymous')
              AND invoice_date < TIMESTAMP '{cutoff_sql}'
            """
        )
        connection.execute(
            f"""
            CREATE VIEW outcome_sales AS
            SELECT * FROM transactions
            WHERE reason_code = 'sale_identified'
              AND invoice_date >= TIMESTAMP '{cutoff_sql}'
              AND invoice_date < TIMESTAMP '{end_sql}'
            """
        )
        _copy_query(
            connection,
            """
            SELECT customer_id, stock_code,
                   COUNT(DISTINCT invoice_no) AS invoice_count,
                   COUNT(*) AS purchase_lines,
                   MAX(invoice_date) AS last_purchase,
                   LN(1 + COUNT(DISTINCT invoice_no)) AS log_invoice_weight
            FROM history_sales
            GROUP BY customer_id, stock_code
            """,
            snapshot_dir / "interactions.parquet",
        )
        _copy_query(
            connection,
            f"""
            WITH base AS (
                SELECT customer_id,
                       MIN(invoice_date) AS first_purchase,
                       MAX(invoice_date) AS last_purchase,
                       COUNT(DISTINCT invoice_no) AS frequency_invoices,
                       COUNT(DISTINCT stock_code) AS distinct_products,
                       COUNT(DISTINCT CAST(invoice_date AS DATE)) AS active_days,
                       SUM(line_value) AS monetary_gbp,
                       FIRST(country ORDER BY invoice_date DESC, raw_row_id DESC) AS country
                FROM history_sales GROUP BY customer_id
            ),
            scored AS (
                SELECT *,
                       DATE_DIFF('day', last_purchase, TIMESTAMP '{cutoff_sql}') AS recency_days,
                       NTILE(4) OVER (ORDER BY last_purchase ASC, customer_id) AS r_score,
                       NTILE(4) OVER (ORDER BY frequency_invoices ASC, customer_id) AS f_score,
                       NTILE(4) OVER (ORDER BY monetary_gbp ASC, customer_id) AS m_score
                FROM base
            )
            SELECT *,
                   CASE
                       WHEN r_score >= 3 AND f_score >= 3 THEN 'recent_frequent'
                       WHEN r_score >= 3 THEN 'recent'
                       WHEN f_score >= 3 THEN 'frequent'
                       ELSE 'less_recent_less_frequent'
                   END AS rfm_segment
            FROM scored
            """,
            snapshot_dir / "customers.parquet",
        )
        _copy_query(
            connection,
            f"""
            WITH catalog AS (
                SELECT stock_code,
                       MIN(invoice_date) AS first_seen,
                       MAX(invoice_date) AS last_sale,
                       COUNT(DISTINCT customer_id) AS historical_customers,
                       COUNT(*) AS sale_lines,
                       COUNT(DISTINCT CASE WHEN invoice_date >= TIMESTAMP '{cutoff_sql}' - INTERVAL 90 DAY
                           THEN customer_id END) AS popularity_90d,
                       FIRST(description ORDER BY
                           CASE WHEN description IS NOT NULL THEN 0 ELSE 1 END,
                           invoice_date DESC, raw_row_id DESC) AS description_as_of_cutoff
                FROM history_sales
                GROUP BY stock_code
            )
            SELECT stock_code, COALESCE(description_as_of_cutoff, stock_code) AS description,
                   first_seen, last_sale, historical_customers, sale_lines, popularity_90d
            FROM catalog
            """,
            snapshot_dir / "products.parquet",
        )
        _copy_query(
            connection,
            "SELECT raw_row_id, invoice_no, stock_code, description, quantity, "
            "invoice_date, unit_price, customer_id, country, line_value "
            "FROM analytics_sales",
            snapshot_dir / "analytics_sales.parquet",
        )
        _copy_query(
            connection,
            f"""
            SELECT raw_row_id, invoice_no, stock_code, quantity, invoice_date,
                   unit_price, customer_id, country, line_value, reason_code
            FROM transactions
            WHERE reason_code IN ('cancellation', 'nonpositive_quantity')
              AND quantity < 0 AND unit_price > 0
              AND invoice_date < TIMESTAMP '{cutoff_sql}'
            """,
            snapshot_dir / "adjustments.parquet",
        )
        _copy_query(
            connection,
            """
            SELECT customer_id, stock_code,
                   MIN(invoice_date) AS first_outcome_time,
                   COUNT(DISTINCT invoice_no) AS future_invoices
            FROM outcome_sales
            GROUP BY customer_id, stock_code
            """,
            outcome_dir / "labels.parquet",
        )
        counts = {
            "history_identified_lines": connection.execute(
                "SELECT COUNT(*) FROM history_sales"
            ).fetchone()[0],
            "history_analytics_lines": connection.execute(
                "SELECT COUNT(*) FROM analytics_sales"
            ).fetchone()[0],
            "customers": connection.execute(
                "SELECT COUNT(DISTINCT customer_id) FROM history_sales"
            ).fetchone()[0],
            "candidate_products": connection.execute(
                "SELECT COUNT(DISTINCT stock_code) FROM history_sales"
            ).fetchone()[0],
            "interactions": connection.execute(
                "SELECT COUNT(*) FROM (SELECT DISTINCT customer_id, stock_code FROM history_sales)"
            ).fetchone()[0],
            "future_identified_lines": connection.execute(
                "SELECT COUNT(*) FROM outcome_sales"
            ).fetchone()[0],
            "future_customers": connection.execute(
                "SELECT COUNT(DISTINCT customer_id) FROM outcome_sales"
            ).fetchone()[0],
        }
    finally:
        connection.close()
    manifest = {
        "snapshot_id": snapshot_id,
        "name": name,
        "cutoff": cutoff.isoformat(),
        "outcome_end_exclusive": outcome_end.isoformat(),
        "source_hash": source_hash,
        "policy": policy,
        "counts": counts,
        "service_artifacts": [
            "interactions.parquet",
            "customers.parquet",
            "products.parquet",
            "analytics_sales.parquet",
            "adjustments.parquet",
        ],
        "outcome_artifacts": ["labels.parquet"],
    }
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    config.reports_dir.mkdir(parents=True, exist_ok=True)
    summary_path = config.reports_dir / "snapshots.json"
    summaries = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else {}
    summaries[name] = {
        "snapshot_id": snapshot_id,
        "cutoff": cutoff.isoformat(),
        "outcome_end_exclusive": outcome_end.isoformat(),
        "counts": counts,
        "source_hash": source_hash,
    }
    summary_path.write_text(json.dumps(summaries, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest
