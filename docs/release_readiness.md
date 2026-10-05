# V1 release readiness

This checklist combines prior merged-main evidence through `d3fa6d6` with local designed-dashboard checks on 2026-10-05. The current branch changes are not yet merged or released. [Issue #10](https://github.com/thaitrongdang/RetailMind/issues/10) tracks remaining acceptance work.

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
| GitHub CI on merged main | `done` | [CI run 37133659899](https://github.com/thaitrongdang/RetailMind/actions/runs/37133659899) succeeded on `96cfb1e`. |
| Designed-dashboard PR CI | `in_progress` on final head | [PR #14](https://github.com/thaitrongdang/RetailMind/pull/14) previously passed `fixture-tests` and `container-build` on `b6f4de4` in [run 37344804127](https://github.com/thaitrongdang/RetailMind/actions/runs/37344804127); final-head checks, merge and main CI still to verify. |
| Local API benchmark | `done` | `reports/api_benchmark.json`; p95 109.029 ms over 200 sequential loopback requests, 20 warmups, one worker. |
| Docker image build and API import | `done` | [CI run 37134339279](https://github.com/thaitrongdang/RetailMind/actions/runs/37134339279) passed `container-build` on PR #13. |
| Compose launch with real mounted bundles | `blocked` | Docker, Podman and nerdctl unavailable on this host; test `compose.yaml` on a Docker host with locally built snapshot/model artifacts. |
| Final video and public V1 release | `planned` | Screenshots exist; video, designed-UI PR/CI, Compose with real bundles and final release check remain. No tag/release yet. |

**Current boundary:** Backend and designed UI are usable locally. The project must not be described as released V1 until the current branch has passed PR/CI and remaining applicable verification is recorded. Public hosting remains optional and needs an explicit destination/cost decision.
