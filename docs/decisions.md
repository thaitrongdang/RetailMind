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

## 2026-10-03 — Frozen test interpretation

- **Decision:** Keep ItemCF as the selected serving model after test. Report ALS separately.
- **Reason:** Selection was fixed by validation NDCG@10 before opening test. Test ItemCF had NDCG@10 0.166409; ALS had 0.151927. ALS had higher Recall@10 (0.081083 versus 0.072709), but changing the selection criterion after test would contaminate the holdout.
- **Evidence:** `reports/validation_selection.json`, `reports/test_metrics.json`, `reports/model_card.md` and `reports/test_error_analysis.json`.
- **Limit:** This is retrospective purchase overlap, not online benefit.

## 2026-10-03 — Read-only API boundary

- **Decision:** Load snapshot-specific model bundles once in FastAPI lifespan; keep future labels behind a separate replay route. Give every response a request ID and expose ranking scores with explicit semantics.
- **Reason:** Rebuilding a model per request would change latency and risk mixing cutoffs. The UI needs a stable contract for real and failure states. Explicit new-customer mode prevents a mistyped historical ID silently becoming Popularity.
- **Evidence:** `src/retailmind/service.py`, `src/retailmind/api.py` and `tests/test_api.py`. Real-bundle smoke checks covered both snapshots, success paths, CSV and 404/422/503 cases. A 200-request loopback benchmark is recorded in `reports/api_benchmark.json`.
- **Limit:** The benchmark is sequential and local. Public security, traffic and deployment behavior remain unmeasured.

## 2026-10-03 — Frontend and container verification

- **Decision:** Keep the final frontend framework and layout open until the owner supplies the visual design. Expose overview, customer, product, quality, evaluation and replay data through Python API routes so the frontend can be implemented without duplicating business logic. Prepare Docker files now and mark the build unverified.
- **Reason:** The design may need more customization than Streamlit; the original plan's default should be reconsidered from the actual handoff. Docker is not installed on this host.
- **Evidence:** Frontend handoff requested asynchronously; `Dockerfile` and `compose.yaml` written, `docker --version` reported command not found.
## 2026-10-03 — Provisional inspection UI

- **Decision:** Serve a small six-page HTML/CSS/JS interface from FastAPI at `/ui/` while waiting for the owner's final design. It calls the existing API and keeps all recommendation logic on the Python side.
- **Reason:** This allows the snapshot, model, new-customer, replay, product, evaluation and quality flows to be exercised now without committing to Streamlit or a separate frontend framework before seeing the design.
- **Evidence:** `ui/` and `scripts/smoke_ui_logic.cjs`. The smoke script exercised all six controllers, validation/test switching, ALS selection, explicit new-customer mode and an unknown-customer error against the real local API; JavaScript syntax and Python checks passed.
- **Limit:** The browser automation tool was blocked by an automatic usage-limit review and then a Windows sandbox helper failure, so the visual desktop/mobile interaction check and screenshots remain pending. This interface is explicitly provisional and is not the approved design.

## 2026-10-05 — Designed dashboard adaptation

- **Decision:** Keep the existing FastAPI-served HTML/CSS/JavaScript frontend and adapt it to the visual tokens and page behavior in `DESIGN.md` and `RetailMind_Frontend_Brief.md`. The brief resolves conflicts with the Factory marketing reference. A desktop sidebar, mobile navigation drawer, dark data panels and selective light summary panels serve the six analytical pages.
- **Reason:** The written handoff asks for substantial styling control but does not require React, Tailwind or Streamlit. The existing frontend already consumes the stable API. Keeping that small stack avoids a second server and keeps recommendation logic entirely in Python.
- **Alternatives considered:** Streamlit, the original default, would require framework-specific layout work for this sidebar and detailed responsive shell. A separate JavaScript framework would add a build and dependency layer without a product requirement that needs it.
- **Evidence:** The six pages were exercised with real API data in Chrome at 1440×900 and 390×844. Screenshots are in `docs/screenshots/`. The browser check covered snapshot switching, replay reveal, page navigation and horizontal overflow. `scripts/smoke_ui_logic.cjs` checks the controller flow independently.
- **Limit:** `DESIGN.md` is a written style reference, not a pixel-level screen design. The app uses the declared system font fallback where Geist is unavailable. Browser verification covers Chrome on one machine; a wider accessibility and cross-browser audit remains useful.

## 2026-10-05 — Data quality audit details

- **Decision:** Include raw-field missingness and up to three traceable sample rows per classification reason in the aggregate data-quality report. Generate both from the raw/classified Parquet pipeline and expose them through the existing read-only quality endpoint.
- **Reason:** Counts alone could not show which source rows produced a reason or distinguish raw missing values from the exclusive primary classification reason. The sample uses `raw_row_id`, sheet and Excel row number for reproducible lookup.
- **Evidence:** `src/retailmind/data/ingest.py`, `tests/test_ingest.py`, regenerated `reports/data_quality.json` and the Data Quality page.
