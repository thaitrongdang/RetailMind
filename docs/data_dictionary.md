# Data dictionary and grain

## Source and prepared data

| Field | Grain and meaning |
| --- | --- |
| `raw_row_id` | One workbook row, identified by workbook SHA-256 prefix, zero-based sheet index, and one-based Excel row number. |
| `source_sheet`, `source_row` | Original sheet name and row number for audit. |
| `invoice_no` | Invoice identifier; not unique for a line. A leading C/c signals cancellation. |
| `stock_code` | Product or charge code, stored as text. |
| `invoice_date` | Source local-clock timestamp; timezone not specified. |
| `quantity`, `unit_price` | Parsed quantity and unit price in GBP. |
| `customer_id` | Nullable identifier. Missing IDs remain missing. |
| `line_value` | Quantity multiplied by unit price; positive merchandise sales and eligible negative adjustments are shown separately. |
| `reason_code` | Exactly one classification reason per source row. |

Classification priority is invalid date, missing invoice or product code, invalid quantity or price, cancellation, nonpositive quantity or price, configured non-merchandise code, anonymous merchandise sale, or identified merchandise sale. Source duplicate-like rows are flagged in aggregate but retained pending sensitivity analysis.

## Snapshot tables

| Artifact | Grain | Definition |
| --- | --- | --- |
| `customers.parquet` | snapshot ID + customer ID | Pre-cutoff positive merchandise purchases; first/last purchase, RFM, active days and distinct products. Frequency counts distinct invoices, not lines. |
| `products.parquet` | snapshot ID + stock code | Candidate product with pre-cutoff description, first/last sale, all-history distinct customers, and 90-day distinct-customer popularity. |
| `interactions.parquet` | snapshot ID + customer ID + stock code | Distinct invoice count, purchase lines, last purchase and log invoice weight. |
| `analytics_sales.parquet` | snapshot ID + source row | Positive merchandise sales before cutoff, including rows without customer ID. |
| `adjustments.parquet` | snapshot ID + source row | Eligible negative-quantity cancellations/adjustments before cutoff, not back-applied to older snapshots. |
| `outcomes/<snapshot_id>/labels.parquet` | snapshot ID + customer ID + stock code | Distinct valid future purchases in the 30-day window; unavailable to recommendation serving. |

## KPI definitions

- **Positive merchandise sales value (GBP):** sum of `line_value` for pre-cutoff analytics sales. This is not audited revenue or profit.
- **Eligible adjustment value (GBP):** sum of negative `line_value` in the adjustment artifact. Show separately from positive sales value.
- **Sales invoices:** distinct `invoice_no` among positive analytics sales.
- **Identified customers:** distinct non-null `customer_id` among identified positive sales.
- **Catalog products:** distinct `stock_code` among identified positive merchandise sales.
- **Recency:** days between a customer's latest qualifying sale and the cutoff.
- **Frequency:** number of distinct qualifying sale invoices.
- **Monetary:** sum of positive qualifying merchandise line values.
- **Average order value:** positive sales value divided by distinct sales invoices, never by line count.
