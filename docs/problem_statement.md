# Problem statement

## Decision to support

For an identified customer at cutoff time `t`, rank up to 10 products the customer may purchase in `[t, t + 30 days)`. Use only information with transaction time `< t`. Previously purchased products remain eligible because repeat purchases are part of the task. A model score orders products; it is not a probability of purchase.

## Units and boundaries

| Unit | Meaning | Example |
| --- | --- | --- |
| Transaction line | One source spreadsheet row for one product on an invoice | Invoice `A100`, product `SKU-A` |
| Invoice | A transaction grouping that may contain several lines | `A100` contains `SKU-A` and `SKU-B` |
| Customer | An identified buyer that may have multiple invoices | `C1` has invoices `A100` and `A101` |
| Customer-product interaction | Qualified purchase evidence aggregated for one customer and product before the cutoff | `C1` bought `SKU-A` on two invoices |

`InvoiceNo` cannot uniquely identify a line. Ingestion will assign a raw row ID from the source file, sheet, and original row position. Missing customer IDs will not be combined into one invented customer.

The main label for an eligible customer is the set of distinct valid products purchased in the next 30 days. The cutoff belongs to the label window, not the training history; the endpoint `t + 30 days` is excluded. The candidate set contains valid merchandise with identified sales before the cutoff. It approximates products known from transactions, not stock availability. Future-only products remain in the denominator of the main Recall@10 metric.

## Hand-counted cutoff example

Run `examples/granularity_example.py` with the project Python environment. At the 2011-09-01 00:00:00 cutoff, the three earlier rows form two invoices (A100 and A101), one known customer (C1), and two distinct interactions (C1 with SKU-A and SKU-B). C1 bought SKU-A on two invoices, yet it remains one distinct customer-product pair in this count.

The row exactly at the cutoff is a future outcome, so C2 is not a known customer at prediction time. C1 buys SKU-B again after the cutoff; this repeat purchase can be a valid future label. SKU-C appears only at the cutoff, so it cannot enter the earlier candidate set.

## Planned evaluation

The provisional validation cutoff is `2011-09-01 00:00:00`; the provisional test cutoff is `2011-11-01 00:00:00`. Both require verification against the source workbook, including whether each full 30-day outcome window is observable. The data's timezone is not specified, so timestamps will retain source values without an invented timezone.

All compared models will use the same cutoff, candidate set, repeat policy, labels, and customer cohort. Validation selects the configuration. Test is evaluated after that choice is fixed. Customers with history but no valid future purchase are counted separately and excluded from ranking metrics rather than given zero recall.

## Limits of inference

Purchase history does not show every product a customer saw. Offline matches against later purchases cannot establish increased sales. The dataset does not establish inventory status or actual product availability at the cutoff.
