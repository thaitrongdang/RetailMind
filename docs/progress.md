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

### 2026-10-06 — Designed dashboard merged and demo recorded

**GitHub:** [PR #14](https://github.com/thaitrongdang/RetailMind/pull/14) final head `a92874841065fee95c7699ab19faa13e30c43d09` passed `fixture-tests` and `container-build` in [run 37346100259](https://github.com/thaitrongdang/RetailMind/actions/runs/37346100259). The PR was squash-merged as `bab9cdcf3b859432a74d390784e757429b7a0e10`; local `main` fast-forwarded cleanly to `origin/main`. [Merged-main CI run 37346331288](https://github.com/thaitrongdang/RetailMind/actions/runs/37346331288) completed successfully. No V1 tag or public deployment has been created.

**Demo and reporting:** Recorded `docs/demo/retailmind-walkthrough.webm` from the real local API and six-page UI. Playwright's FFmpeg probe reported a 2:00.32 VP8 video at 1280×720 and 25 fps; sample frames were visually inspected. It is silent with on-screen captions. Updated README, case study and release checklist to reflect the merged PR and measured demo, without claiming a Compose run or business lift.

**Readiness:** Backend, frozen offline evaluation, designed UI, real-data browser flows, screenshots, demo recording and GitHub CI are `done`. Real-bundle Docker Compose launch is `blocked` on this machine because Docker, Podman and nerdctl are absent. Public release is `blocked` pending that packaging check and a final release review. Continue with documentation and local verification while a Docker host is unavailable.

**Delivery checkpoint:** [PR #15](https://github.com/thaitrongdang/RetailMind/pull/15) added the two-minute video and updated handoff docs. Its final head `d834e15c4b81bfdd6767c5fa75dcae0b21767509` passed `fixture-tests` and `container-build` in [run 37348576246](https://github.com/thaitrongdang/RetailMind/actions/runs/37348576246), then squash-merged as `4d6751f6220769a06f5efae5c1c7ce411193ad25`. Local `main` fast-forwarded. [Merged-main CI run 37348822558](https://github.com/thaitrongdang/RetailMind/actions/runs/37348822558) completed successfully. This checkpoint does not change the measured offline reports.

## 2026-10-07 — Compose prerequisites and independent acceptance

**Repository checkpoint:** Initial working tree was clean. Fetch confirmed local `main`, `origin/main` and HEAD all at `11a79da86d235d3f767133b1547322a5ccec9962`. Remote remains `https://github.com/thaitrongdang/RetailMind.git`. GitHub confirms PR #15 merged at `4d6751f`, its final-head run 37348576246 successful, and current checkpoint-main run 37349670227 successful. PR #16's merged commit is `11a79da`. No release exists. New work is on `codex/v1-compose-verification`.

| Scope | State | Actual evidence / next action |
| --- | --- | --- |
| Prior offline pipeline and frozen model evaluation | `done` | Reused existing bundles; source SHA-256 matches, 1,067,371 rows reconcile; all history/product/customer timestamps precede cutoff and label timestamps fit the 30-day windows. Model card table matches frozen JSON metrics. No retraining or numeric evaluation-report change. |
| Current local API/UI checks | `done` | Fresh Uvicorn process on port 8766 with both real bundles; 39 HTTP checks, six UI controllers and Chrome desktop/mobile flow passed. |
| Compose health/mount safeguards and verification command | `done` implementation | Healthcheck requires both snapshots; missing bind source paths rejected; `scripts/verify_compose.py` checks read-only mounts, host/container bundle hashes, serving files, commit and actual API behavior. CI validated Compose configuration and image/import on PR #18. Docker-dependent real-bundle execution is pending. |
| Docker engine / real-bundle Compose | `blocked` | No Docker/Podman/nerdctl. Windows 11 Pro 22H2 build 22621.2134 is below current Docker Desktop requirements; WSL/VMP features disabled. See `docs/docker_setup.md`. |
| v1.0.0 | `blocked` | Do not tag until real-bundle Compose and final clean-commit CI/acceptance pass. |

**Measured host prerequisites:** Dell Latitude 7480, Intel i7-7600U x64, 17,057,779,712 bytes installed RAM; firmware virtualization and SLAT supported/enabled. Hypervisor is not active. `Win32_OptionalFeature` reports InstallState 2 (disabled) for VirtualMachinePlatform and Microsoft-Windows-Subsystem-Linux. `wsl --version` displays inbox help; `wsl --status` exits 50. `LanmanServer` is Running/Automatic. Current official Docker docs require a supported Windows 11 build 22631 or later and WSL >=2.1.5. User action: update Windows to a supported release, install modern WSL in an Administrator shell, reboot as requested, install/start Docker Desktop with Linux containers, then confirm both Client/Server in `docker version`. No OS installation or reboot was performed.

**Implementation:** Added `scripts/smoke_api.py` (standard-library HTTP verification against existing reports/metadata) and `scripts/verify_compose.py` (real mount hashes, container health, image serving-file hashes, unchanged bundles, clean-commit gate). Compose now has a two-snapshot healthcheck and explicit read-only bind mounts with `create_host_path: false`. `.dockerignore` excludes leftover environments, temporary browser profiles and delivery docs. CI validates normalized Compose configuration. An acceptance review found recommendation endpoints accepted k=20 despite the V1 maximum of ten; both now enforce 1..10, with fixture and real-HTTP boundary checks. Product similarity's independent neighbor limit remains documented.

**Commands/results actually run:** Under CPython 3.12.14 with OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=4, `python -m pytest tests -q --basetemp=.pytest_tmp_compose -p no:cacheprovider` passed 11 tests (one Starlette/AnyIO deprecation warning); `ruff check src tests scripts`, compileall, Node syntax and `git diff --check` passed. `python scripts/smoke_api.py --base-url http://127.0.0.1:8766 --output .uv-cache/api_verification_20261007.json` passed 39 HTTP checks, including both snapshots, selected/Popularity/ItemCF/ALS, model versions, CSV, explicit new customer, 404/422, frozen report equality, temporal bounds and unchanged ranking after outcomes. `RETAILMIND_API_URL=http://127.0.0.1:8766; node scripts/smoke_ui_logic.cjs` passed. Chrome exercised all six pages at 1440x900 and 390x844, CSV, unknown-ID recovery, new-customer mode, test-to-validation switching, one outcomes request after reveal and mobile keyboard navigation; no unexpected console/page errors or page-level horizontal overflow. Recheck captures are ignored in `.uv-cache/browser-shots-20261007`.

**Delivery audit:** Thirteen tracked PNGs are valid desktop/mobile captures. Existing video probes as VP8 1280x720, 25 fps, 2:00.32, 7,543,667 bytes; a sample frame was visually inspected. README, model card, case study and API contract now reflect actual verification and top-ten behavior. `reports/verification_20261007.json` records source/bundle hashes and local acceptance with `release_commit_verified=false`. `python scripts/verify_compose.py --output .uv-cache/compose_verification_20261007.json` returned `status=blocked`, exit 1, because Docker CLI is absent; no container run is claimed.

**Next actions:** When a Docker host is available, fetch the current verified main and run `python scripts/verify_compose.py --require-clean` on the exact candidate commit, then run the UI checks against the container on port 8000. Record actual image/commit IDs and results, complete final review, verify candidate CI and only then create GitHub v1.0.0. Public hosting remains optional.

**GitHub scope:** [Issue #17](https://github.com/thaitrongdang/RetailMind/issues/17) tracks Compose preparation and outstanding real-bundle acceptance. Issue #10 remains open. GitHub's releases list and remote tags were rechecked and empty. The branch has not yet been pushed at this entry.

**PR/CI update:** Commit `d0ca6082d9ce1f4020c81926d6a27e81a321fbc5` was pushed, and [PR #18](https://github.com/thaitrongdang/RetailMind/pull/18) was opened/attached. [Run 37646269053](https://github.com/thaitrongdang/RetailMind/actions/runs/37646269053) completed successfully, including fixture tests, Compose configuration validation, Docker image build and API import. The clean-commit preflight `python scripts/verify_compose.py --require-clean --output .uv-cache/compose_candidate_verification_20261007.json` recorded `working_tree_clean=true` for `d0ca608` and `status=blocked` because Docker CLI is absent. This documentation follow-up is checked on its new PR head before merge; the real-bundle Compose gate remains blocked.

**Merged-main checkpoint:** PR #18 final head `0cc3f9195f51f65a4a7717dcb91701174974e2f7` passed [run 37646684957](https://github.com/thaitrongdang/RetailMind/actions/runs/37646684957), then squash-merged as `eab0a79764efea678efa51fcc6e8a321024e6a4f`. Local `main` fast-forwarded; `main`, `origin/main` and HEAD matched with a clean tree. [Main run 37646931964](https://github.com/thaitrongdang/RetailMind/actions/runs/37646931964) completed successfully. A clean-commit preflight on `eab0a79` again returned `blocked` because Docker CLI is unavailable, recorded in ignored `.uv-cache/compose_main_verification_20261007.json`. No Docker-dependent acceptance or v1.0.0 release is claimed. The new local API process on port 8766 served the checked top-ten contract; the earlier verification process on 8765 was stopped. The next dependency is the user's supported Docker/WSL setup or another Docker host with these same bundles.

## 2026-10-11 — Supported Docker-host handoff

**Checkpoint:** Owner reports Windows Update offers no upgrade. CIM still reports Windows 11 Pro build 22621; Docker CLI is absent. Fetch and GitHub API confirmed local/main/origin at `aa717e03ada08c0ba2e3c52281257e426f332c5e`, merged PR #19 and successful main CI run 37647681830. GitHub releases are empty. Initial working tree contained a pre-existing edit in `docs/docker_setup.md` (`wwwthe`); it is preserved and excluded from this work's commits. New scope is on `codex/v1-docker-host-handoff`, advancing existing Issue #17.

**Independent work, in_progress:** Added a standard-library archive/hash handoff tool (`scripts/transfer_bundles.py`), promoted the prior local Chrome flow into a portable `scripts/smoke_browser.cjs`, and documented candidate selection, private transfer, host-local Compose execution, loopback SSH tunneling and evidence return in `docs/docker_host_handoff.md`. Updated README and readiness links; CI checks the new browser script's syntax. No raw data, model retraining, frozen metric changes or container pass is claimed. Source environment remains CPython 3.12 in `.uv-cache/venv`; global Python 3.14 is newly present but outside the package's >=3.11,<3.14 range.

**Blocked / owner input:** Need an existing supported Docker host, OS/architecture, Docker/Compose outputs, writable checkout path, and either owner-run commands or a locally configured SSH alias with permission to transfer/build/run. A paid host is not provisioned or assumed. Compose, container UI verification and release remain blocked until those real runs produce evidence on the selected clean commit.

**Independent checks, done:** CPython 3.12 fixture suite passed 11 tests with one existing AnyIO deprecation warning; Ruff, script compile, browser syntax and diff checks passed. A fresh local Uvicorn on 8767 served both real bundles: `scripts/smoke_api.py` passed 39 HTTP checks, `scripts/smoke_ui_logic.cjs` passed, and the portable browser script passed all six desktop/mobile pages with CSV, explicit new customer, expected 404/recovery, snapshot switch, gated reveal and no unexpected errors/overflow. The first browser run checked drawer position mid-transition and failed; the script now waits for the actual closed position, and rerun passed. No UI implementation change was needed.

**Transfer verification, done locally only:** Draft export/check used `.uv-cache/host-transfer-draft-20261011`: 24 required files, 24,616,593 uncompressed bytes, 23,807,299 archive bytes. Every tar member hash matched the existing source bundle. A local check rejected four negative cases: bundle hash, archive hash, commit mismatch and dirty-checkout gate. Draft source cleanliness is false and `compose_verified=false`; re-export from the final clean candidate before transfer. No host was accessed and no file was transferred remotely. `scripts/verify_compose.py --output .uv-cache/compose_preflight_20261011.json` returned blocked, exit 1, for missing Docker. Aggregate evidence is `reports/verification_20261011.json`; frozen evaluation reports remain unchanged. Handoff code/docs are ready for scoped PR/CI; GitHub push/merge is pending at this entry.

**GitHub handoff:** Commit `81cf4cb339a7bbd90dc455927e342bc412603e5e` was pushed on the scoped branch and [PR #20](https://github.com/thaitrongdang/RetailMind/pull/20) opened/attached. Commit initially failed because Git identity was absent after reinstall; the verified existing author identity was supplied per command, without changing global settings. The user edit in `docs/docker_setup.md` remains unstaged. Final-head CI and merge are pending at this checkpoint; neither closes the real-bundle runtime gate.

**Merged handoff checkpoint:** PR #20 final head `40373d7c428959d19e24fc791221f4f6a105df5d` passed [run 38075579656](https://github.com/thaitrongdang/RetailMind/actions/runs/38075579656), then squash-merged as `cb5ebae9c8c086a95111b103fcee99121c5b50a4`. Local main fast-forwarded to origin/main, retaining only the owner's existing `docs/docker_setup.md` edit. [Merged-main CI run 38075693764](https://github.com/thaitrongdang/RetailMind/actions/runs/38075693764) succeeded. Handoff preparation is done; supported-host selection/transfer, real-bundle Compose, container browser verification and exact-release-commit acceptance remain blocked. No host input has arrived at this entry. The temporary API used for independent checks on 8767 was stopped. This documentation checkpoint is prepared on `codex/v1-host-handoff-checkpoint` and changes no source or bundle.
