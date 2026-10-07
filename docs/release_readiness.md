# V1 release readiness

This checklist combines measured offline results, local designed-dashboard checks, and merged-main evidence through `11a79da`, rechecked on 2026-10-07. The current Compose-verification branch has new local checks recorded in `reports/verification_20261007.json`; its PR/CI status is recorded separately in `docs/progress.md`. [Issue #10](https://github.com/thaitrongdang/RetailMind/issues/10) tracks remaining acceptance work. No V1 release has been tagged.

| Acceptance item | State | Evidence or next action |
| --- | --- | --- |
| UCI workbook provenance and all rows reconciled | `done` | `reports/data_manifest.json`, `reports/data_quality.json`; 1,067,371 unique raw row IDs. |
| Cutoff-safe validation/test snapshots and separated labels | `done` | `reports/snapshots.json`, fixture invariance tests. |
| Three comparable models and validation-only selection | `done` | `reports/validation_selection.json`; ItemCF chosen by NDCG@10. |
| Frozen final test and error analysis | `done` | `reports/test_metrics.json`, `reports/test_error_analysis.json`, `reports/model_card.md`. |
| Read-only API with explicit customer/error states and CSV | `done` locally | `tests/test_api.py`, 39 real-bundle HTTP checks in `scripts/smoke_api.py`, `docs/api_contract.md`; recommendation k capped at 10. |
| Six functional page flows | `done` locally | `ui/`, `scripts/smoke_ui_logic.cjs` against real API; replay outcomes requested only on reveal. |
| Supplied written visual design and responsive acceptance | `done` locally | `DESIGN.md` and `RetailMind_Frontend_Brief.md` adapted to the six-page app; Chrome checked 1440×900 and 390×844 with no page overflow. Written reference is not a pixel-exact Figma screen. |
| Browser visual interaction and screenshots | `done` locally | Headless Chrome exercised page navigation, outcome reveal and snapshot switching with no console/page errors. Thirteen real-data screenshots are in `docs/screenshots/`. Cross-browser audit remains outside this check. |
| Fresh Python environment, fixture tests and lint | `done` locally | Recovery sync of 37 locked packages under CPython 3.12.14; 11 tests and Ruff/compile passed again on 2026-10-07. Old `.venv` paths are broken after reinstall. |
| GitHub CI on merged checkpoint main | `done` | [CI run 37349670227](https://github.com/thaitrongdang/RetailMind/actions/runs/37349670227) succeeded on `11a79da`; remote state rechecked on 2026-10-07. |
| Designed-dashboard PR CI | `done` | [PR #14](https://github.com/thaitrongdang/RetailMind/pull/14) passed `fixture-tests` and `container-build` on final head `a928748` in [run 37346100259](https://github.com/thaitrongdang/RetailMind/actions/runs/37346100259), then squash-merged as `bab9cdc`. |
| Local API benchmark | `done` | `reports/api_benchmark.json`; p95 109.029 ms over 200 sequential loopback requests, 20 warmups, one worker. |
| Docker image build and API import | `done` | [CI run 37134339279](https://github.com/thaitrongdang/RetailMind/actions/runs/37134339279) passed `container-build` on PR #13. |
| Compose launch with real mounted bundles | `blocked` | Docker unavailable; Windows 11 22H2 build 22621 is below current Docker Desktop requirements; WSL/VMP features disabled. Follow `docs/docker_setup.md`, then run `scripts/verify_compose.py --require-clean` on the release candidate. Preflight returned blocked on 2026-10-07; Docker-dependent stages have not run. |
| Captioned demo video | `done` locally | `docs/demo/retailmind-walkthrough.webm` records the real local API and six-page UI; silent captions, VP8 1280×720. |
| GitHub v1.0.0 release | `blocked` | Real-bundle Compose launch remains unverified. Verify all applicable gates and CI on the exact clean release commit before tagging. No tag/release exists. Public hosting is optional. |

**Current boundary:** Backend and designed UI are usable locally and merged with passing CI. A real-bundle Compose check is still needed before claiming a fully verified packaged V1. Public hosting remains optional and needs an explicit destination/cost decision.

## Resume gate

Once Docker is installed and its Linux engine is running, run the clean-commit Compose command from `docs/docker_setup.md`. Confirm `status=passed`, both loaded snapshots, read-only mount/hash checks, `/ui/`, rankings and expected API errors. Run the UI controller/browser flow against port 8000 and preserve the JSON evidence with commit and image IDs. Documentation-only readiness updates may require a new candidate commit; recheck that final clean commit before creating `v1.0.0`. The local 2026-10-07 report explicitly records `release_commit_verified=false`.
