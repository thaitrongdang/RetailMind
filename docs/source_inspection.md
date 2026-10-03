# Source inspection checklist

Status: planned. No source workbook is present in the workspace yet.

1. Download the Online Retail II workbook from the [UCI dataset page](https://archive.ics.uci.edu/dataset/502/online+retail+ii). Record the page URL, retrieval date, published license, and exact local filename. Keep the workbook unchanged under `data/raw/`.
2. Compute SHA-256 for the workbook and record the hash in a data manifest. The manifest must not include a private machine path.
3. List every sheet, its headers, and its data-row count. Confirm whether the two periods use different header spellings before mapping columns into `invoice_no`, `stock_code`, `description`, `quantity`, `invoice_date`, `unit_price`, `customer_id`, and `country`.
4. Inspect source types and representative values. Keep invoice, product, and customer IDs as strings; check Excel numeric customer IDs for a trailing `.0` after conversion.
5. Count missing values, cancellation invoices, negative or zero quantities, nonpositive prices, invalid dates, and suspicious duplicate lines by sheet. Do not discard rows while making this inventory.
6. Record minimum and maximum valid timestamps and verify both provisional cutoff windows in the problem statement are fully observable. Preserve source clock values; the timezone is unknown.
7. Define `raw_row_id` using workbook hash, sheet name, and original sheet row number. Verify it is unique across all sheets. Do not use invoice number as a row key.
8. Compare total rows in the manifest against sheet counts and subsequent raw Parquet output. Keep separate counts for analytics-eligible sales, identified sales for recommendations, and adjustments once cleaning rules are implemented.

The ingestion pipeline, manifest, and checks will be implemented in the next data session after the workbook is available.
