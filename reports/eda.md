# Cutoff-safe exploratory findings

These figures come from `GET /overview?snapshot=test`, which queries `analytics_sales.parquet` built strictly before 2011-11-01. Sales include identified and anonymous customers, valid merchandise, positive quantity and price; cancellations and other adjustments are excluded. `gross_sales_gbp` is a positive-sale total, not net revenue or profit.

1. The pre-cutoff analytic slice has 928,987 sale lines, 35,956 distinct invoice numbers, 5,633 identified customers and 4,867 product codes. The recommendation candidate set is smaller at 4,595 codes because it requires identified historical sales.
2. October 2011 has 2,006 invoices and GBP 1,106,719.54 gross positive sales, versus 1,818 invoices and GBP 1,030,500.36 in September. This is a month-to-month observation within the available history, not a forecast or causal seasonal claim.
3. The United Kingdom accounts for GBP 15,422,314.78 of the GBP 18,083,913.15 pre-cutoff gross total (about 85.3%). This source is strongly UK weighted; country patterns elsewhere have smaller samples.
4. Stock code `85123A` appears on 5,049 invoices, the largest invoice count in the top-products query. Stock code `21212` has 93,476 units versus 90,422 for `85123A`; units and invoice frequency answer different questions.
5. The top five countries by gross positive sales are United Kingdom, EIRE, Netherlands, Germany and France. Their invoice counts are 32,966, 529, 198, 672 and 517 respectively. Country ranking by value differs from ranking by invoice count, so the dashboard labels both measures and their units.

Reproduce with `uv run python -c "from retailmind.config import load_config; from retailmind.service import load_services; from retailmind.analytics import overview; print(overview(load_services(load_config())[0]['test']))"` after building the snapshots and model bundles. The API also returns monthly and country tables for exact figures.