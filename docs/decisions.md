# Decision log

## 2026-10-03 — Initial local environment

- **Decision:** Use the already installed CPython 3.11.15 in a project-local `.venv` for Session 1.
- **Reason:** Python 3.11 is available locally and the isolated environment can be created offline. The first example needs no third-party packages.
- **Alternatives considered:** The default `python` command points to Anaconda Python 3.14.6; a local Python 3.13.5 is also installed. Dependency compatibility has not been checked for the later pipeline, so no project package versions are pinned yet.
- **Evidence:** `uv python list --only-installed` and successful `uv venv .venv --python 3.11 --offline` on 2026-10-03.
## 2026-10-03 — Known non-merchandise stock codes

- **Decision:** Exclude the exact stock codes POST, M, C2, ADJUST, ADJUST2, BANK CHARGES, D, DOT, TEST001, and TEST002 from paid-merchandise recommendations. Preserve every raw row and count these lines under `non_merchandise`.
- **Reason:** In identified positive sales strictly before the validation cutoff (2011-09-01), their observed descriptions identify postage, carriage, manual charges, adjustments, bank charges, discounts, dotcom postage, or test products. POST occurred in 1,397 such lines, M in 592, and C2 in 196. The smaller codes were also observed before the cutoff.
- **Alternatives considered:** Excluding every nonstandard alphanumeric code would wrongly remove merchandise including 15056BL, 79323LP, PADS, and SP1002. Keeping every code would allow service fees and test products as candidates.
- **Evidence:** DuckDB query on `data/processed/transactions.parquet`, filtered to `reason_code = 'sale_identified'` and `invoice_date < '2011-09-01'`, grouped by stock code and description. The exact exclusion list is stored in `configs/project.yaml`.
- **Limit:** This is a source-specific V1 policy based on pre-validation history. Newly seen non-merchandise codes after validation may need a future versioned rule and must not be selected using test outcomes.
## 2026-10-03 — Validation model and fallback selection

- **Decision:** Select ItemCF with 20 item neighbors, log(1 + distinct invoice count) interaction weighting, and minimum 1 historical invoice for personalized serving. Popularity remains the explicit new-customer and insufficient-score fallback.
- **Reason:** On the common validation cohort of 1,071 returning historical customers, ItemCF achieved NDCG@10 0.202483 and Recall@10 0.095172. Popularity had NDCG@10 0.103128; the best ALS configuration in the limited search had NDCG@10 0.157450. Routing thresholds 2 and 3 lowered NDCG@10 to 0.195252 and 0.188809.
- **Alternatives considered:** ItemCF 20/50 neighbors with binary/log weighting; ALS 32/64 factors and regularization 0.05/0.2, with 10 iterations, one confidence scale and seed 42; Popularity 90-day baseline.
- **Evidence:** `reports/validation_selection.json` contains every search result, cohort definition, frozen evaluation contract and selected parameters. The saved ItemCF bundle reproduced validation NDCG@10 exactly after reload.
- **Limit:** Offline validation does not demonstrate revenue lift. The configuration is frozen before test and must not be changed based on test performance.
