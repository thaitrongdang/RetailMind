"""Cutoff-safe aggregate queries for the inspection UI."""

from __future__ import annotations

import duckdb

from retailmind.service import SnapshotService


def overview(service: SnapshotService) -> dict:
    path = str((service.catalog.snapshot_dir / "analytics_sales.parquet").resolve()).replace("\\", "/").replace("'", "''")
    connection = duckdb.connect()
    try:
        connection.execute(f"CREATE VIEW sales AS SELECT * FROM read_parquet('{path}')")
        summary = connection.execute("""
            SELECT COUNT(*) AS sale_lines,
                   COUNT(DISTINCT invoice_no) AS invoices,
                   COUNT(DISTINCT customer_id) AS identified_customers,
                   COUNT(DISTINCT stock_code) AS products,
                   ROUND(SUM(line_value), 2) AS gross_sales_gbp
            FROM sales
        """).fetchone()
        monthly = connection.execute("""
            SELECT STRFTIME(invoice_date, '%Y-%m') AS month,
                   COUNT(DISTINCT invoice_no) AS invoices,
                   COUNT(*) AS sale_lines,
                   ROUND(SUM(line_value), 2) AS gross_sales_gbp
            FROM sales GROUP BY 1 ORDER BY 1
        """).fetchall()
        countries = connection.execute("""
            SELECT country, COUNT(DISTINCT invoice_no) AS invoices,
                   ROUND(SUM(line_value), 2) AS gross_sales_gbp
            FROM sales GROUP BY 1 ORDER BY gross_sales_gbp DESC, country LIMIT 20
        """).fetchall()
        top_products = connection.execute("""
            SELECT stock_code, COUNT(DISTINCT invoice_no) AS invoices,
                   SUM(quantity) AS units
            FROM sales GROUP BY 1 ORDER BY invoices DESC, stock_code LIMIT 20
        """).fetchall()
    finally:
        connection.close()
    return {
        "snapshot_id": service.snapshot_id,
        "train_cutoff": service.manifest["cutoff"],
        "scope": "all_positive_valid_merchandise_sales_before_cutoff_including_anonymous",
        "gross_sales_definition": "sum_positive_line_value_gbp_excludes_returns_and_adjustments",
        "summary": dict(zip(("sale_lines", "invoices", "identified_customers", "products", "gross_sales_gbp"), summary)),
        "monthly": [dict(zip(("month", "invoices", "sale_lines", "gross_sales_gbp"), row)) for row in monthly],
        "countries": [dict(zip(("country", "invoices", "gross_sales_gbp"), row)) for row in countries],
        "top_products": [dict(zip(("stock_code", "invoices", "units"), row)) for row in top_products],
    }