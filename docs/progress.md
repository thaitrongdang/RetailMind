# Progress

## 2026-10-03 — Week 1, Session 1

**Status:** `in_progress` (technical setup complete; learner explanation is pending).

**Goal:** Define the 30-day top-10 ranking problem, create an isolated Python environment, prepare a minimal project structure, and practice the initial GitHub workflow.

**Completed:** Read the full project plan. The workspace initially held only `RetailMind_Codex_Plan.md`, with no repository or source workbook. Created `.venv` with CPython 3.11.15, wrote the README and problem statement, prepared the source inspection checklist, and ran the granularity example. Initialized local Git, connected `origin`, pushed `main`, created Issue #1, and completed a small branch and PR.

**Files changed:** `.gitignore`, `README.md`, `docs/problem_statement.md`, `docs/source_inspection.md`, `docs/decisions.md`, `docs/learning_log.md`, `docs/progress.md`, and `examples/granularity_example.py`. The original plan was retained unchanged.

**Commands run and observed results:**

- `uv python list --only-installed`: Python 3.11.15, 3.13.5, and 3.14.6 were available.
- `uv venv .venv --python 3.11 --offline`: created the project-local environment.
- `.\.venv\Scripts\python.exe --version`: `Python 3.11.15`.
- `.\.venv\Scripts\python.exe -c "import sys, pathlib, hashlib; print(sys.executable); print('stdlib imports OK')"`: standard-library imports succeeded.
- `.\.venv\Scripts\python.exe examples\granularity_example.py`: 3 history lines, 2 invoices, 1 customer, 2 distinct customer-product interactions, and 2 future lines.
- `git init -b main`: initialized the local repository on `main`.
- `git diff --check`: passed for the documentation PR.
- `git push -u origin main`: initial local commits reached GitHub; local and remote `main` both pointed to `ae5fc9c` when checked.
- `git push -u origin docs/granularity-example`: branch commit `cb9228d` reached GitHub.
- `git pull --ff-only origin main`: local `main` advanced to merge commit `8d3f7b3` and matched `origin/main`.

**GitHub state:** Repository: [RetailMind](https://github.com/thaitrongdang/RetailMind). Initial local commits `de65ec9` and `ae5fc9c` were pushed. [Issue #1](https://github.com/thaitrongdang/RetailMind/issues/1) is closed as completed. [PR #2](https://github.com/thaitrongdang/RetailMind/pull/2) was self-reviewed and squash-merged; GitHub reported merge commit `8d3f7b3`. CI is `planned` for Week 3 and has not run.

**Learning check:** The learner has not yet submitted their own explanation or variant of the granularity example. The source workbook is absent, so no data manifest or dataset counts have been produced.

**Review topics:** Explain line versus invoice versus customer versus interaction; identify which rows belong before a cutoff; distinguish local commit from push to GitHub.

**Next task:** Review the learner's exercise, then obtain and inspect the UCI source workbook, verify its sheet schema and time coverage, and begin the raw ingestion session.
## 2026-10-03 — V1 implementation mode checkpoint

**Status:** `in_progress`. The user's new direction is to build all of V1 first and study afterward; the old Session 1 exercise is no longer an implementation gate. Learner-authored explanations remain pending.

**Phase checklist**

| Phase | Status | Evidence |
| --- | --- | --- |
| Foundation and repository | `in_progress` | Existing GitHub remote inspected; CPython 3.11.15, uv 0.11.28, project package and `uv.lock` established. Foundation branch has not yet been merged. |
| Ingestion and quality | `done` locally | Both UCI sheets streamed; 1,067,371 rows reconcile to unique row IDs and reason counts. Fixture idempotence checks passed. |
| SQL and snapshots | `done` locally | Validation/test snapshots built; cutoff and future-invariance fixtures passed. Outcomes stored separately. |
| Baseline and evaluator | `done` locally | Hand-counted metric fixtures passed; real Popularity validation measured. |
| ItemCF, ALS, validation selection | `done` locally | Four ItemCF and four ALS configurations evaluated on validation; ItemCF 20 neighbors with log weighting selected. |
| Frozen test and error report | `planned` | Selection contract frozen; final test command has not run. |
| API and frontend contract | `planned` | No API or service tests yet. |
| User-designed frontend | `planned` | Design handoff requested; independent backend work continues. |
| Packaging, CI, portfolio | `planned` | No clean-environment run or release claim yet. |

**Environment/source:** Windows 10.0.22000; approximately 14.94 GB process-reported available memory at inspection and 257 GB free on drive D. The UCI ZIP was downloaded from the official dataset page into ignored `data/raw/`. Workbook SHA-256: `bcbe73b35f5b7babf197fb0cb983a11f5d9ff929078d4aa53d171b1f2df2e980`; 45,622,278 bytes. Sheets: Year 2009-2010 (525,461 data rows) and Year 2010-2011 (541,910). Observed valid timestamps: 2009-12-01 07:45:00 through 2011-12-09 12:50:00.

**Quality reconciliation:** `sale_identified=802651`, `sale_anonymous=234460`, `non_merchandise=4559`, `cancellation=19494`, `nonpositive_quantity=3457`, `nonpositive_price=2750`; sum = 1,067,371. Suspicious duplicate extra rows: 34,335, flagged but retained. Exact non-merchandise codes were selected from pre-validation history and recorded in decisions.

**Snapshot counts:** Validation cutoff 2011-09-01: 5,224 historical customers, 4,405 candidates, 387,138 interactions, 39,870 future identified sale lines. Test cutoff 2011-11-01: 5,633 historical customers, 4,595 candidates, 439,624 interactions, 64,301 future identified sale lines. These are build counts, not model metrics.

**Validation selection:** Main cohort has 1,071 historical customers with future labels; 4,153 historical customers have empty labels and are reported separately; 188 future customers were unseen at cutoff. Popularity: Recall@10 0.041157, NDCG@10 0.103128. Selected ItemCF (20 neighbors, log invoice weighting): Recall@10 0.095172, NDCG@10 0.202483. Best ALS among the limited search: NDCG@10 0.157450. Validation chose minimum 1 historical invoice for personalized routing. All metrics are offline matches, not revenue effects.

**Checks actually run:** `retailmind inspect`, `retailmind prepare` (one initial run and one run with the finalized exclusion policy), `retailmind build-snapshot --snapshot validation`, `retailmind build-snapshot --snapshot test`, `retailmind train --snapshot validation`, `python -m compileall -q src`, and `python -m pytest tests -q --basetemp=.pytest_tmp_all --durations=5` (10 passed). Loaded validation bundles matched mapping hashes; re-evaluating the saved ItemCF bundle reproduced NDCG@10 exactly. The system Temp directory caused an initial pytest permission error; workspace-local basetemp resolved it.

**GitHub state:** Remote remains `https://github.com/thaitrongdang/RetailMind.git`; `main` was clean at commit `da2c374` before this work. Branch `feat/v1-data-foundation` contains uncommitted implementation and the user's previously untracked `AGENTS.md`. [Issue #4](https://github.com/thaitrongdang/RetailMind/issues/4) has been created for foundation acceptance. No V1 branch push, PR, CI, or merge has been claimed yet.

**Next actions:** Review diff and commit the foundation phase through GitHub. Run frozen test evaluation once, analyze cohorts and errors, then implement API and six-page frontend. Request any missing design detail only when integration depends on it.

## 2026-10-03 — Frozen test, API and packaging checkpoint

**Status:** `in_progress`. Backend and local API are functioning; final design and six-page frontend are pending. Docker build verification and GitHub CI status are pending.

| Phase | Status | Evidence |
| --- | --- | --- |
| Foundation and repository | `done` | PR #5 squash-merged to `main` at `87c0bee`; source, lockfile, data/model fixtures and aggregate validation reports tracked. |
| Ingestion, quality, SQL and snapshots | `done` | 1,067,371 source rows reconcile; two cutoff snapshots and separated outcomes built. |
| Models and validation selection | `done` | Popularity, ItemCF and ALS evaluated on common validation cohort; ItemCF frozen by NDCG@10. |
| Final test and error report | `done` | Test report written once from frozen selection; model card and failure slices recorded. |
| API and contract | `done` locally | Both real bundles load; routes, validation, CSV, request IDs and log tested; fixture API test passed. |
| User-designed frontend | `blocked` for final layout | Bundled design handoff requested from owner; independent API/packaging work continued. |
| Packaging and portfolio | `in_progress` | CI workflow and Docker files written; fresh environment and HTTP benchmark passed; Docker command unavailable; GitHub CI run still to verify. |

**Frozen test:** Test snapshot `test-20111101-bcbe73b35f5b-1cfa8347816f` has 5,633 historical customers and 4,595 candidate products. Main ranking cohort has 1,469 historical customers with future labels; 4,164 historical customers have empty labels and 191 future customers are new. Selected ItemCF achieved Recall@10 0.072709, NDCG@10 0.166409 and HitRate@10 0.573860. Popularity NDCG@10 was 0.114242; ALS 0.151927. ALS Recall@10 was higher than ItemCF, but the validation selection was not changed. Label availability was 99.216% micro. These are offline outcomes only.

**Error analysis:** 626/1,469 selected-model customers had no top-10 overlap with observed future purchases. Of 49,463 future customer-product pairs, 388 were future-only candidates and 21,478 were repeat purchases. The analysis was generated by `retailmind analyze-errors --snapshot test`; its first CLI invocation did not dispatch due to a missing branch, which was fixed before the successful run. No test model was retrained.

**API checks:** Actual saved validation/test bundles loaded at startup. Smoke requests to `/health`, `/snapshots`, `/customers/12384`, `/recommendations`, `/recommendations/new`, `/products`, `/products/22423/similar`, `/evaluations`, `/replay/outcomes`, `/overview`, `/data-quality` and `/evaluations/errors` returned HTTP 200. Unknown customer and snapshot returned 404; invalid k returned 422; CSV recommendation/evaluation exports returned 200. `tests/test_api.py` verifies fallback, repeat-item metadata, request ID and missing-model 503 on a small fixture. Future labels are read only in the replay route.

**Reproducibility and performance:** FastAPI 0.118.0, Uvicorn 0.37.0 and Ruff 0.13.1 added with pinned lockfile. `UV_PROJECT_ENVIRONMENT=.venv_clean; uv sync --locked --python 3.11 --extra dev` installed 37 packages in a fresh environment; 11 tests passed and `ruff check src tests` passed. A real local Uvicorn HTTP benchmark with 20 warmups and 200 sequential top-10 requests against 20 deterministic historical customers measured startup-to-ready 2,385.166 ms, p50 32.264 ms, p95 109.029 ms and max 196.923 ms on Windows 10, CPython 3.11.15 and four logical CPUs. This is not a UI or concurrent load measurement. `docker --version` reported that Docker is not installed, so the image and Compose files remain unverified.

**GitHub state at checkpoint:** Branch `feat/v1-evaluation-api` is local and contains uncommitted work. The previous foundation PR #5 is merged. [Issue #6](https://github.com/thaitrongdang/RetailMind/issues/6) has been created for this scope. The new CI workflow has not yet run on GitHub; no PR or release for this branch is claimed here.

**Next actions:** Review and commit this scoped backend/report change, push and open a PR; verify CI and merge. Integrate the supplied frontend design into six functional pages, test desktop/mobile and snapshot switching, then verify Docker where available and prepare final screenshots, demo, case study and V1 release only after the whole project passes acceptance.
**GitHub update:** Commit `cf89ab1` was pushed on `feat/v1-evaluation-api`; [PR #7](https://github.com/thaitrongdang/RetailMind/pull/7) was opened and attached to the Codex task. [CI run 37128965178](https://github.com/thaitrongdang/RetailMind/actions/runs/37128965178) completed successfully; its `fixture-tests` job passed. The PR is pending a small API contract documentation update and final self-review/merge. No V1 release or final frontend is claimed.