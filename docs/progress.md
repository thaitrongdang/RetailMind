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
## 2026-10-03 — Provisional six-page UI checkpoint

**Status:** `in_progress`. Final design integration is still `blocked` by the missing owner handoff; a functional provisional inspection UI is implemented locally.

**GitHub:** PR #7 passed its latest [CI run 37129134360](https://github.com/thaitrongdang/RetailMind/actions/runs/37129134360), was squash-merged to `main` as commit `548d1ff7c9ea15872808e1e6cff0117f7b47c316`, and local `main` was fast-forwarded cleanly. Branch `feat/v1-provisional-ui` was created from that commit; [Issue #8](https://github.com/thaitrongdang/RetailMind/issues/8) tracks this scoped UI work. This branch currently has uncommitted UI changes; no UI PR/CI/merge or release is claimed yet.

**Implementation:** `ui/index.html`, `ui/style.css` and `ui/app.js` provide six provisional pages served at `/ui/`: Overview, Customers, Historical Replay, Products, Model Evaluation and Data Quality. All visible figures come from real API routes. Snapshot and model selection, explicit new-customer mode, CSV downloads, evidence, observed replay labels, loading/empty/error states and mobile CSS are included. The frontend does not implement recommendation algorithms. `Dockerfile` now copies UI assets. CI gains JavaScript syntax checks.

**Checks:** `node --check ui/app.js` passed; Python compile and Ruff checks passed. A hidden local Uvicorn server responded 200 at `/health`, `/ui/` and `/ui/app.js`. `node scripts/smoke_ui_logic.cjs` exercised all six page controllers over the real local HTTP API, switched to validation, selected ALS, opened new-customer mode and verified unknown-customer error handling. These are DOM-light integration checks, not visual browser validation.

**Browser blocker:** The `agent-browser` CLI is unavailable. The available browser-control tool was first rejected by automatic approval review due to a usage limit, then its runtime failed with `windows sandbox failed: helper_unknown_error: setup refresh had errors`. No browser interaction or screenshot was obtained. Desktop/mobile visual acceptance remains pending, as does the owner-supplied final design. Continue non-visual tests and documentation; do not claim the final V1 frontend is complete.

**Next actions:** Commit this provisional UI in a scoped PR, verify CI and merge. When the owner supplies the design, implement the agreed final layout/framework, run real browser checks and screenshots, then verify Docker on a Docker host and complete the V1 delivery materials/release.
**UI PR update:** Commit `e0972f3` was pushed and [PR #9](https://github.com/thaitrongdang/RetailMind/pull/9) opened/attached. [CI run 37133393046](https://github.com/thaitrongdang/RetailMind/actions/runs/37133393046) completed successfully with `fixture-tests` passing, including Node syntax checks. An evidence-backed English case-study draft has been added locally; PR #9 will be updated and rechecked before merge. Final design, visual browser check, Docker verification, video and release remain pending.
## 2026-10-03 — Verified merged-main checkpoint

**Status:** Backend `done`; provisional UI `done` for API-flow inspection; overall V1 `in_progress`, with final frontend design and visual/container acceptance `blocked` by concrete missing inputs/tooling. The owner has been asked again for a bundled Figma/screenshots/template handoff with any required assets, framework preference and mobile behavior; independent work continued.

**GitHub:** [PR #9](https://github.com/thaitrongdang/RetailMind/pull/9) passed [CI run 37133530209](https://github.com/thaitrongdang/RetailMind/actions/runs/37133530209) on its final head and was squash-merged as `96cfb1e61bc486213ce9a42309d56e06d112848e`. Local `main` fast-forwarded cleanly. [CI run 37133659899](https://github.com/thaitrongdang/RetailMind/actions/runs/37133659899) on that merged `main` commit completed successfully; Issues #6 and #8 were verified closed. No release tag or hosting deployment exists.

**Actual checks at this point:** 11 Python fixture tests passed (one dependency deprecation warning); Ruff and Python compile passed. Node syntax passed. The provisional six-page controller smoke script passed against the real HTTP API, including two snapshot contexts, ALS model, new-customer route and unknown ID error. A browser visual check was attempted but not completed due to the automatic approval usage-limit failure followed by Windows sandbox helper initialization failure. Docker/Podman/nerdctl commands are absent. Neither screenshots nor a container run are claimed.

**Next actions:** Implement the owner's final visual design and agreed framework, verify six pages at desktop/mobile widths with real browser interaction and snapshot switching, test Docker Compose on a host with Docker, capture screenshots/demo video, update case study from draft, then run final acceptance checks and create v1.0.0 only when all required criteria pass. [Issue #10](https://github.com/thaitrongdang/RetailMind/issues/10) tracks these remaining acceptance items. See `docs/release_readiness.md` for exact state.
## 2026-10-03 — GitHub container build verification

**Status:** Docker image build and API import `done` on a GitHub-hosted Linux runner; Compose with real mounted bundles remains `blocked` locally because no Docker/Podman/nerdctl runtime is available. [Issue #12](https://github.com/thaitrongdang/RetailMind/issues/12) and [PR #13](https://github.com/thaitrongdang/RetailMind/pull/13) scope the change. [CI run 37134339279](https://github.com/thaitrongdang/RetailMind/actions/runs/37134339279) reported both `fixture-tests` and `container-build` successful for commit `93354e5`. The container job ran `docker build --tag retailmind:ci .` and imported `retailmind.api` from `/app/.venv/bin/python` inside the resulting image. This verifies packaging/import, not readiness with the ignored real snapshot and model volumes. Documentation is being updated before PR merge; no final release is claimed.

## 2026-10-05 — Recovery checkpoint after local app reinstall

**Status:** `in_progress`. Read repository instructions, plan, design brief, README, progress and release checklist. Current branch `feat/v1-designed-dashboard` points to `d3fa6d6`, matching local `main` and `origin/main` at inspection. Remote is `https://github.com/thaitrongdang/RetailMind.git`. Existing changes were preserved: modified `ui/app.js`, `ui/index.html`, `ui/style.css`; untracked `DESIGN.md`, `RetailMind_Frontend_Brief.md` and `tmp/`. The temporary Chrome profile under `tmp/` is not project source and must not be committed.

| Scope | State | Evidence / next action |
| --- | --- | --- |
| Data ingestion, snapshots, validation and frozen test | `done` in prior runs | Tracked reports and prior test/CI checkpoints exist; recheck integrity and tests on this machine after environment restoration. |
| API and container image build | `done` in prior runs | Source, API tests and CI Docker import recorded above; local API run still to reverify. |
| Designed six-page frontend | `in_progress` | New written `DESIGN.md` and `RetailMind_Frontend_Brief.md` now supply design direction; three UI files have uncommitted adaptation work. Finish all pages and browser verification. |
| Local Compose with real bundles, screenshots, final release | `blocked` or `planned` | No local container runtime observed yet; browser and release acceptance pending. |

**New-machine dependency finding:** PowerShell 7.6.5, Git 2.53.0 and Node 24.19.0 are callable. `python` resolves to the Windows Store alias; `py`, `uv`, `gh` and `npm` are absent from PATH. Both old `.venv` and `.venv_clean` contain uv trampolines that fail to spawn their former Python base (`entity not found`). A bundled Codex Python runtime has been located but not yet evaluated for project compatibility. Recreate a project environment from the pinned `uv.lock`; do not treat old environments as working.

**Immediate next actions:** Inspect modified UI and available runtime, restore Python/uv locally, run fixture checks and real API/UI smoke tests, finish design adaptation, perform desktop/mobile browser checks, then update README, release readiness and this checkpoint with observed results. Git reports a dubious-ownership warning after reinstall; read-only commands used per-invocation `safe.directory` without changing global Git configuration.

### 2026-10-05 — Recovery and designed UI verification update

**Local state:** The written design handoff has been implemented on the existing FastAPI-served six-page UI. `ui/app.js`, `ui/index.html`, `ui/style.css` and `ui/favicon.svg` provide the shared dark shell, responsive navigation, snapshot context, real status, chart/table styling, model summary, quality audit and errors. Replay now loads history and a cutoff-time ranking first, then calls the separate outcomes endpoint only after `Reveal outcomes`. The frontend does not train or score models. `DESIGN.md` and `RetailMind_Frontend_Brief.md` are retained as source design documents. Existing user UI edits were extended in place.

**Data quality:** `src/retailmind/data/ingest.py` now writes raw-field missing counts and up to three lineage examples per primary reason; the fixture test checks both. `retailmind prepare` completed on the actual workbook with the same SHA-256 and 1,067,371 source rows, all unique and reconciled. Measured raw missing values: `customer_id_raw=243007`, `description_raw=4382`; the other six raw fields each have zero missing values. This updates `reports/data_quality.json` but does not refit a model or alter the frozen test report.

**Environment and commands:** Installed `uv==0.11.28` into ignored `.uv-cache/tools` using the bundled CPython 3.12.14, then ran `uv sync --locked --python <bundled-python> --extra dev` with `UV_PROJECT_ENVIRONMENT=.uv-cache/venv`. The locked sync installed 37 packages. `.uv-cache/venv/Scripts/uvicorn.exe retailmind.api:app --host 127.0.0.1 --port 8765` started successfully; `/health` reported `ready` with validation and test bundles, and `/ui/` returned HTTP 200. Standard `python`, `uv` and `gh` commands still need normal installation or PATH configuration for README commands in a fresh terminal. Existing `.venv` directories remain untouched and nonfunctional after reinstall.

**Checks actually run:** Workbook SHA-256 matched `reports/data_manifest.json`. `python -m pytest tests -q --basetemp=.pytest_tmp_final -p no:cacheprovider` passed 11 tests with one Starlette/AnyIO deprecation warning; Ruff, Python compile, Node syntax and `git diff --check` passed. `node scripts/smoke_ui_logic.cjs` passed all six controllers, validation switch, unknown customer and reveal gating against the real local API. Headless Chrome checked all six pages at 1440×900 and 390×844, one outcome request only after reveal, test-to-validation switching, no document-level horizontal overflow and no browser console/page errors. Thirteen real-data screenshots are in `docs/screenshots/`. This is a Chrome check on one machine, not a cross-browser audit.

**Current readiness:** Backend and designed six-page frontend are `done` locally. Overall V1 remains `in_progress`: branch work is uncommitted at this checkpoint; push/PR/CI on the designed UI, local Compose with mounted bundles, demo video and release verification remain. Docker/Podman/nerdctl and `gh` are not installed on this machine. Continue with scoped GitHub review and documentation; never imply the earlier Docker image CI tested mounted real bundles.

**GitHub and interaction update:** Commit `bcd1eef` was pushed on `feat/v1-designed-dashboard`. An additional browser pass found that 404 for an unknown customer left no way to edit the ID; commit `b6f4de4` adds `Change customer ID` and extends the smoke check. Chrome then passed CSV download, explicit new-customer mode, expected 404 and recovery, six pages, mobile drawer closure, reveal gating and snapshot switching. [PR #14](https://github.com/thaitrongdang/RetailMind/pull/14) was opened and attached to this task. [CI run 37344804127](https://github.com/thaitrongdang/RetailMind/actions/runs/37344804127) completed successfully on `b6f4de4`, with `fixture-tests` and `container-build` passing. PR review/merge and merged-main CI remain pending at this entry.

**Mobile keyboard follow-up:** Browser review also found that the closed mobile drawer could remain keyboard-focusable. `ui/app.js` now makes the closed drawer inert and hidden from assistive technology, restores it when opened, and closes it with Escape while returning focus to the menu button. The real Chrome check passed those states, all six pages, CSV, expected customer 404/recovery, snapshot switching and outcome reveal again. This follow-up is awaiting its final PR-head CI at this entry.
