# V1 release readiness

This checklist records observed state after merged `main` commit `96cfb1e61bc486213ce9a42309d56e06d112848e`. It is not a release announcement. [Issue #10](https://github.com/thaitrongdang/RetailMind/issues/10) tracks the remaining acceptance work.

| Acceptance item | State | Evidence or next action |
| --- | --- | --- |
| UCI workbook provenance and all rows reconciled | `done` | `reports/data_manifest.json`, `reports/data_quality.json`; 1,067,371 unique raw row IDs. |
| Cutoff-safe validation/test snapshots and separated labels | `done` | `reports/snapshots.json`, fixture invariance tests. |
| Three comparable models and validation-only selection | `done` | `reports/validation_selection.json`; ItemCF chosen by NDCG@10. |
| Frozen final test and error analysis | `done` | `reports/test_metrics.json`, `reports/test_error_analysis.json`, `reports/model_card.md`. |
| Read-only API with explicit customer/error states and CSV | `done` | `tests/test_api.py`, real-bundle HTTP smoke, `docs/api_contract.md`. |
| Six functional page flows | `in_progress` | `ui/`, `scripts/smoke_ui_logic.cjs` against real API; explicitly provisional. |
| Final supplied visual design and responsive acceptance | `blocked` | Owner design handoff requested. Implement agreed layout and test desktop/mobile. |
| Browser visual interaction and screenshots | `blocked` | Browser-control automatic approval review hit usage limit; retry after reset failed because Windows sandbox helper could not initialize. No screenshots have been verified. |
| Fresh Python environment, fixture tests and lint | `done` | Locked install of 37 packages; 11 tests and Ruff passed locally. |
| GitHub CI on merged main | `done` | [CI run 37133659899](https://github.com/thaitrongdang/RetailMind/actions/runs/37133659899) succeeded on `96cfb1e`. |
| Local API benchmark | `done` | `reports/api_benchmark.json`; p95 109.029 ms over 200 sequential loopback requests, 20 warmups, one worker. |
| Docker build and Compose launch | `blocked` | Docker, Podman and nerdctl unavailable on this host. Build and exercise `compose.yaml` on a Docker host. |
| Final screenshots/video and public V1 release | `planned` | Capture and review after final design, browser and container checks. No tag/release yet. |

**Current boundary:** Backend and provisional UI are usable locally. The project must not be described as fully complete V1 or released until final design integration and applicable verification pass. Public hosting remains optional and needs an explicit destination/cost decision.