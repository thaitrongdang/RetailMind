# RetailMind: time-aware product recommendations from retail transactions

> Portfolio draft based on verified backend results. Replace the provisional UI section and add reviewed screenshots/video only after the owner-provided final design and browser checks are complete.

## Problem

A retail transaction table contains purchases, not recommendation exposures. RetailMind asks a narrow offline question: given a customer's valid transactions before a historical cutoff, which up to ten products are most likely to overlap with valid purchases observed in the following 30 days? Repeat purchases are eligible. The result is a ranked list for a historical demo, not a purchase probability or a claim of incremental sales.

## Source and preparation

The project uses the UCI Online Retail II workbook, licensed CC BY 4.0. Both sheets contain 1,067,371 rows in total. A source-hash-backed row ID links each prepared record to its sheet and Excel row. The pipeline preserves raw columns, classifies every line into one auditable reason and reconciles all 1,067,371 unique row IDs. It identified 802,651 valid customer-linked merchandise sale lines and 234,460 valid anonymous lines, alongside cancellations, nonpositive quantity/price and non-merchandise charges. Duplicate-like lines were flagged and retained rather than silently removed.

Missing customer IDs remain missing. Anonymous sales contribute to aggregate analytics but never become one artificial shared recommendation user. Source timestamps have no specified timezone, so the pipeline does not label them UTC.

## Temporal design

Validation history ends strictly before 2011-09-01; test history ends strictly before 2011-11-01. Each outcome window starts at its cutoff and ends 30 days later, exclusive. Each snapshot has its own customer and product mappings, descriptions, 90-day popularity, ItemCF similarities and ALS factors. Future labels live in a separate outcome directory and are never loaded by the recommendation service. This prevents the common error of replaying a past date with a model trained on later data.

The validation candidate catalog contained 4,405 products; the test catalog contained 4,595. All three models rank the full catalog, allow repeats and use the same cohort and future labels. Main Recall@10 includes future products not yet in the catalog; eligible recall and label availability show this catalog limit separately.

## Models and selection

Popularity ranks codes by distinct customers in the prior 90 days. ItemCF uses sparse customer-product invoice counts, log weighting and cosine item similarity with self-similarity removed. ALS uses implicit feedback with confidence scaling applied once and checks user/item factor axes against saved mappings. Bundles contain snapshot IDs and mapping hashes; loading fails on a mismatch.

A limited validation search compared four ItemCF and four ALS configurations. Validation NDCG@10 selected ItemCF with 20 neighbors and log invoice weighting. The validation cohort had 1,071 historical customers with future purchases. Selected ItemCF NDCG@10 was 0.202483, compared with Popularity 0.103128 and the best searched ALS 0.157450. This selection and evaluation policy were frozen before opening final test outcomes.

## Final offline result

| Model | Test Recall@10 | Test NDCG@10 | Test HitRate@10 |
| --- | ---: | ---: | ---: |
| Popularity | 0.042627 | 0.114242 | 0.561607 |
| ItemCF, selected | 0.072709 | 0.166409 | 0.573860 |
| ALS | 0.081083 | 0.151927 | 0.599728 |

The test ranking cohort had 1,469 historical customers with at least one future valid purchase. Another 4,164 historical customers had no future label, and 191 future customers were new. ALS exceeded ItemCF on test Recall@10 but not NDCG@10; the project kept the validation-selected ItemCF rather than changing criteria after seeing test results. Of 49,463 distinct future customer-product pairs, 388 were products unavailable at the test cutoff, giving 99.216% micro label availability.

The selected model had no top-ten overlap for 626 of 1,469 evaluated customers (42.614%). The no-hit rate was higher for customers with at most five historical invoices than for those with more than five. This is an offline miss analysis, not evidence that customers saw or rejected recommendations.

## Service and reproducibility

The FastAPI service loads both snapshot bundles read-only at startup. It exposes customers, products, rankings, similarity, metrics, quality, aggregate overview and a separately routed historical outcome reader. Unknown historical IDs return 404; explicit new-customer mode uses Popularity. Responses carry request IDs, actual serving model, version, score semantics, repeat flags and historical evidence. CSV exports include snapshot and evaluation metadata. The six-page inspection UI is provisional until final design approval.

A fresh locked CPython 3.11 environment passed 11 fixture tests and Ruff lint. GitHub Actions CI passed on the merged provisional UI commit on `main` as well as the backend PR. On the development Windows host, a sequential loopback HTTP benchmark of 200 top-ten requests after warmup measured p50 32.264 ms and p95 109.029 ms, with 2,385.166 ms from process launch to readiness. The method used 20 deterministic historical customers, one worker and evidence enabled; it is not a concurrent traffic or UI latency result.

## Limits and next work

The source is historical and represents one retailer with many wholesale-like purchases. It has no impression logs, live inventory, A/B assignment or online feedback. Offline overlap cannot establish click-through rate, conversion, revenue uplift or causal impact. Duplicate sensitivity and performance on a different store remain unmeasured. The final owner-supplied UI, visual browser checks, Docker build, demo recording and release are pending, so this draft is not yet a completed public V1 case study.

Reproduction and detailed evidence: `README.md`, `reports/data_manifest.json`, `reports/data_quality.json`, `reports/validation_selection.json`, `reports/test_metrics.json`, `reports/model_card.md`, `reports/error_analysis.md` and `reports/api_benchmark.json`.