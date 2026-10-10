# V1 release readiness

This checklist combines measured offline results, local designed-dashboard checks, and merged-main evidence through `eab0a79`, rechecked on 2026-10-07. Compose verification preparation and the top-ten API correction were merged in PR #18; local checks are recorded in `reports/verification_20261007.json`. [Issue #10](https://github.com/thaitrongdang/RetailMind/issues/10) and [Issue #17](https://github.com/thaitrongdang/RetailMind/issues/17) track outstanding real-bundle acceptance. No V1 release has been tagged.

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
| GitHub CI on merged implementation main | `done` | [CI run 37646931964](https://github.com/thaitrongdang/RetailMind/actions/runs/37646931964) succeeded on `eab0a79`; local main and origin/main matched cleanly. |
| Designed-dashboard PR CI | `done` | [PR #14](https://github.com/thaitrongdang/RetailMind/pull/14) passed `fixture-tests` and `container-build` on final head `a928748` in [run 37346100259](https://github.com/thaitrongdang/RetailMind/actions/runs/37346100259), then squash-merged as `bab9cdc`. |
| Local API benchmark | `done` | `reports/api_benchmark.json`; p95 109.029 ms over 200 sequential loopback requests, 20 warmups, one worker. |
| Docker image build and API import | `done` in CI | [CI run 37646931964](https://github.com/thaitrongdang/RetailMind/actions/runs/37646931964) passed Compose configuration validation, image build and API import on merged `eab0a79`. This CI job has no real data mounts. |
| Compose launch with real mounted bundles | `blocked` | Docker unavailable; Windows 11 22H2 build 22621 is below current Docker Desktop requirements; WSL/VMP features disabled. Follow `docs/docker_setup.md`, then run `scripts/verify_compose.py --require-clean` on the release candidate. Preflight returned blocked on 2026-10-07; Docker-dependent stages have not run. |
| Captioned demo video | `done` locally | `docs/demo/retailmind-walkthrough.webm` records the real local API and six-page UI; silent captions, VP8 1280×720. |
| GitHub v1.0.0 release | `blocked` | Real-bundle Compose launch remains unverified. Verify all applicable gates and CI on the exact clean release commit before tagging. No tag/release exists. Public hosting is optional. |

**Current boundary:** Backend and designed UI are usable locally and merged with passing CI. A real-bundle Compose check is still needed before claiming a fully verified packaged V1. Public hosting remains optional and needs an explicit destination/cost decision.

## Resume gate

Once Docker is installed and its Linux engine is running, run the clean-commit Compose command from `docs/docker_setup.md`. Confirm `status=passed`, both loaded snapshots, read-only mount/hash checks, `/ui/`, rankings and expected API errors. Run the UI controller/browser flow against port 8000 and preserve the JSON evidence with commit and image IDs. Documentation-only readiness updates may require a new candidate commit; recheck that final clean commit before creating `v1.0.0`. The local 2026-10-07 report explicitly records `release_commit_verified=false`.

## 2026-10-11 handoff checkpoint

The owner reports no Windows upgrade is offered. Local Windows remains build 22621 and Docker CLI is absent. PR #19 is merged as `aa717e03ada08c0ba2e3c52281257e426f332c5e`; [main CI run 37647681830](https://github.com/thaitrongdang/RetailMind/actions/runs/37647681830) is successful, rechecked on 2026-10-11. This is fixture/image CI, not real-bundle Compose acceptance. GitHub's release list is still empty.

The remaining host-dependent steps are explicitly `blocked`: select/access a supported Docker host, privately transfer the existing bundles, execute `scripts/verify_compose.py --require-clean`, verify the UI against that container, and review evidence/CI for the final clean release commit. [docker_host_handoff.md](docker_host_handoff.md) provides the commands and required owner inputs. Transfer hashes and local API/browser checks cannot mark these gates passed. No release is authorized by preparation alone.

Independent checks were rerun on the handoff working branch: 11 tests, Ruff/compile/syntax, 39 real-bundle HTTP checks, UI controllers and portable Chrome desktop/mobile flow passed. Draft archive verification checked 24 source files and rejected hash/commit/dirty-checkout failures. Compose preflight again returned blocked for missing Docker. See `reports/verification_20261011.json`; it explicitly leaves release-commit verification false and records the browser script's initial transition-wait failure and corrected rerun. These local checks do not supersede the pending container gate.
