# V1 release readiness

This checklist combines measured offline results, local designed-dashboard checks, and merged-main evidence through `4d6751f`. [Issue #10](https://github.com/thaitrongdang/RetailMind/issues/10) tracks remaining acceptance work. No V1 release has been tagged.

| Acceptance item | State | Evidence or next action |
| --- | --- | --- |
| UCI workbook provenance and all rows reconciled | `done` | `reports/data_manifest.json`, `reports/data_quality.json`; 1,067,371 unique raw row IDs. |
| Cutoff-safe validation/test snapshots and separated labels | `done` | `reports/snapshots.json`, fixture invariance tests. |
| Three comparable models and validation-only selection | `done` | `reports/validation_selection.json`; ItemCF chosen by NDCG@10. |
| Frozen final test and error analysis | `done` | `reports/test_metrics.json`, `reports/test_error_analysis.json`, `reports/model_card.md`. |
| Read-only API with explicit customer/error states and CSV | `done` | `tests/test_api.py`, real-bundle HTTP smoke, `docs/api_contract.md`. |
| Six functional page flows | `done` locally | `ui/`, `scripts/smoke_ui_logic.cjs` against real API; replay outcomes requested only on reveal. |
| Supplied written visual design and responsive acceptance | `done` locally | `DESIGN.md` and `RetailMind_Frontend_Brief.md` adapted to the six-page app; Chrome checked 1440×900 and 390×844 with no page overflow. Written reference is not a pixel-exact Figma screen. |
| Browser visual interaction and screenshots | `done` locally | Headless Chrome exercised page navigation, outcome reveal and snapshot switching with no console/page errors. Thirteen real-data screenshots are in `docs/screenshots/`. Cross-browser audit remains outside this check. |
| Fresh Python environment, fixture tests and lint | `done` locally | Recovery sync of 37 locked packages under CPython 3.12.14; 11 tests and Ruff passed on 2026-10-05. Old `.venv` paths are broken after reinstall. |
| GitHub CI on merged main | `done` | [CI run 37348822558](https://github.com/thaitrongdang/RetailMind/actions/runs/37348822558) succeeded on `4d6751f`. |
| Designed-dashboard PR CI | `done` | [PR #14](https://github.com/thaitrongdang/RetailMind/pull/14) passed `fixture-tests` and `container-build` on final head `a928748` in [run 37346100259](https://github.com/thaitrongdang/RetailMind/actions/runs/37346100259), then squash-merged as `bab9cdc`. |
| Local API benchmark | `done` | `reports/api_benchmark.json`; p95 109.029 ms over 200 sequential loopback requests, 20 warmups, one worker. |
| Docker image build and API import | `done` | [CI run 37134339279](https://github.com/thaitrongdang/RetailMind/actions/runs/37134339279) passed `container-build` on PR #13. |
| Compose launch with real mounted bundles | `blocked` | Docker, Podman and nerdctl unavailable on this host; test `compose.yaml` on a Docker host with locally built snapshot/model artifacts. |
| Captioned demo video | `done` locally | `docs/demo/retailmind-walkthrough.webm` records the real local API and six-page UI; silent captions, VP8 1280×720. |
| Public V1 release | `blocked` | Real-bundle Compose launch remains unverified on this host. No tag/release or public deployment. |

**Current boundary:** Backend and designed UI are usable locally and merged with passing CI. A real-bundle Compose check is still needed before claiming a fully verified packaged V1. Public hosting remains optional and needs an explicit destination/cost decision.
