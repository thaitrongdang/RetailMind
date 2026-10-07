# RetailMind V1 model card

## Intended use

RetailMind ranks up to ten merchandise stock codes for a customer known at a historical cutoff, for inspection in a portfolio demo. The target is a distinct product purchased in the next 30 days. The score is a ranking signal, not a purchase probability. This is an offline retrospective model, not an experiment or production recommender.

## Data and boundaries

The source is UCI Online Retail II (CC BY 4.0), with 1,067,371 rows across two sheets. Workbook SHA-256: `bcbe73b35f5b7babf197fb0cb983a11f5d9ff929078d4aa53d171b1f2df2e980`. The source has no specified timezone, so timestamps remain local/unspecified. Identified, positive-price, positive-quantity, non-cancellation merchandise sales enter recommendation history. The exact non-merchandise stock-code exclusion list was chosen using pre-validation history and is in `configs/project.yaml`. Duplicate-like rows are flagged and retained.

Validation history is strictly before 2011-09-01; final test history is strictly before 2011-11-01. The corresponding outcomes are from each cutoff inclusive to 30 days later exclusive. Catalogs, mappings, descriptions, popularity, RFM, item similarities and factors are each rebuilt from their own pre-cutoff history. Outcomes are stored separately from service bundles.

## Candidate and evaluation policy

The candidate set contains valid identified merchandise products seen before each cutoff: 4,405 at validation and 4,595 at test. Repeat purchases remain eligible. All three models rank the full candidate set. The main cohort is historical customers with at least one future valid purchase; customers with no future label are counted separately and excluded from main ranking averages. Recall@10 counts all future distinct products, including items that could not be recommended because they were unseen at cutoff. Eligible recall and label availability separately expose that limitation. Results use customer-level macro means.

## Selection and measured results

A limited validation search compared four ItemCF and four ALS configurations against the same Popularity baseline. The validation selection metric was NDCG@10, with a 0.005 absolute simplicity tolerance; ItemCF with 20 neighbors and log invoice weighting was selected. Customers with fewer than one historical invoice would route to Popularity, so no known customer in these snapshots took that fallback. Explicit new-customer requests use Popularity. This choice was frozen before the final test run.

| Split | Model | Evaluated historical customers | Recall@10 | NDCG@10 | HitRate@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| Validation | Popularity | 1,071 | 0.041157 | 0.103128 | 0.484594 |
| Validation | ItemCF, selected | 1,071 | 0.095172 | 0.202483 | 0.647993 |
| Validation | ALS, best searched | 1,071 | 0.093941 | 0.157450 | 0.610644 |
| Test | Popularity | 1,469 | 0.042627 | 0.114242 | 0.561607 |
| Test | ItemCF, frozen selection | 1,469 | 0.072709 | 0.166409 | 0.573860 |
| Test | ALS, best validation configuration | 1,469 | 0.081083 | 0.151927 | 0.599728 |

ALS has higher test Recall@10 than the selected ItemCF, while ItemCF has higher test NDCG@10. The selection is unchanged because test outcomes were reserved for final reporting. Exact configurations, all metrics, cohort tables and timing are in `reports/validation_selection.json` and `reports/test_metrics.json`.

At test, 5,633 customers had eligible history; 4,164 had no future label in the window and 191 future customers were new after cutoff. There were 49,463 distinct future customer-product pairs; 49,075 were in the pre-cutoff candidate set (99.216% micro label availability). Selected ItemCF eligible-label Recall@10 was 0.073092, catalog coverage 0.201306. NDCG@10 by history cohort was 0.138863 for 209 one-invoice customers, 0.133393 for 464 customers with 2–5 invoices, and 0.192887 for 796 customers with more than five invoices.

The reported offline inference p95 in `test_metrics.json` covers model ranking inside evaluation, not HTTP, loading, or UI latency. A separate HTTP benchmark is required for a service latency claim.

## Failure modes and limitations

The selected ItemCF had no top-ten overlap with observed future purchases for 626 of 1,469 evaluated customers (42.614%). The no-hit rate was 50.239% for one-invoice customers, 50.647% for 2–5 invoices and 35.930% for more than five. Of 49,463 future distinct pairs, 388 (0.784%) were products unavailable in the cutoff catalog; 21,478 (43.422%) were repeat purchases. See `reports/test_error_analysis.json` and `reports/error_analysis.md` for reproducible examples and interpretation.

A future purchase mismatch does not mean the customer saw or rejected a recommended product. The historical dataset has no impression, exposure, stock availability or intervention data. Wholesale-like purchasing, missing customer IDs, returns/cancellations, retained duplicate-like lines, short horizon and changing catalog can affect results. The dataset is old and represents one retailer, so generalization to another store or current demand is unmeasured. There is no measured CTR, conversion, revenue gain, fairness outcome or online business impact.

## Reproduction

Run the README pipeline in order. `retailmind train --snapshot validation` selects and records the contract; `retailmind train --snapshot test` uses the frozen selection and refuses to overwrite an existing test report. Bundles carry snapshot ID, mapping hashes, source hash, parameter settings and dependency versions. The public API loads these bundles read-only. Never expose model files or future labels through the recommendation path.

Recommendation HTTP requests enforce `1 <= k <= 10` for historical and explicit new-customer modes. `scripts/smoke_api.py` checks loaded bundle versions, both snapshots, cutoff bounds and API metrics against the already frozen reports. This serving check does not select parameters or recompute test metrics. The 2026-10-07 audit in `reports/verification_20261007.json` checked the source hash, full snapshot timestamp bounds, mappings and this card's metric table.

The separately measured sequential HTTP benchmark is in `reports/api_benchmark.json`, with its original machine/runtime metadata and scope. Current real-bundle Docker Compose acceptance is pending; `docs/docker_setup.md` records the Windows/WSL/Docker prerequisites and the clean-commit verification command. Local HTTP/browser checks and CI image import do not establish real-bundle container readiness.
