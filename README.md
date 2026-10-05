# RetailMind

RetailMind ranks up to 10 products for an identified retail customer at a historical cutoff, using only earlier transactions to predict purchases in the next 30 days. Repeat purchases are eligible. Scores are ranking signals, not purchase probabilities. This repository contains a reproducible offline pipeline, three compared models, a frozen historical evaluation and a read-only API.

## Current status

The data pipeline, two cutoff snapshots, validation selection, frozen test evaluation, model card, error analysis and FastAPI are implemented. The six-page UI at `/ui/` now follows `DESIGN.md` and `RetailMind_Frontend_Brief.md`; its real API flows were checked in Chrome at desktop and mobile widths, including snapshot switching and outcome reveal. The Docker image build and API import passed on GitHub Actions; local Compose with real bundles remains unverified because Docker is unavailable on this host. The current designed-dashboard changes are local and have not yet passed GitHub CI. Public hosting and business impact are not claimed.

## Dataset and protocol

Source: [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii), DOI 10.24432/C5CG6D, CC BY 4.0. The two-sheet workbook and full processed data are ignored by Git. Its verified SHA-256, schema and counts are in [data_manifest.json](reports/data_manifest.json), with cleaning counts in [data_quality.json](reports/data_quality.json). The source timezone is unspecified; timestamps are preserved without assigning UTC.

- Validation cutoff: 2011-09-01; test cutoff: 2011-11-01. History is strictly before its cutoff. Labels are from cutoff inclusive through 30 days later exclusive.
- Candidates are identified valid merchandise products observed before that cutoff. Products unknown at cutoff remain in the denominator of main Recall@10. Eligible recall and label availability are reported separately.
- Main evaluation uses historical customers with at least one future valid purchase; empty-label historical customers and new future customers are accounted for separately. Full candidate lists, common labels/cohorts and repeat policy apply to all models.
- Validation selected ItemCF with 20 neighbors and log invoice weighting by NDCG@10. The test result did not change that choice. See [model_card.md](reports/model_card.md) and the JSON reports for exact metrics and limitations.

| Final test model | Recall@10 | NDCG@10 | HitRate@10 |
| --- | ---: | ---: | ---: |
| Popularity | 0.042627 | 0.114242 | 0.561607 |
| ItemCF, selected | 0.072709 | 0.166409 | 0.573860 |
| ALS | 0.081083 | 0.151927 | 0.599728 |

These are offline matches on 1,469 historical customers with future labels, not online conversion or revenue gains. Test outcome labels are stored apart from service artifacts.

## Reproduce on Windows

Install CPython 3.11 and [uv](https://docs.astral.sh/uv/). From the repository root in PowerShell:

After reinstalling Windows or Python, recreate the virtual environment: a copied `.venv` can retain a path to the old interpreter. This repository's `uv.lock` also supports Python 3.12; the recovery check on 2026-10-05 installed all 37 locked packages with CPython 3.12.14 in an ignored project environment and ran the fixture suite. Git and Node.js are needed for repository work and UI smoke checks; GitHub CLI is optional for the app but useful for PR workflow. Docker is needed only for local Compose verification.

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '4'
uv sync --locked --python 3.11 --extra dev
New-Item -ItemType Directory -Path data/raw -Force | Out-Null
Invoke-WebRequest -Uri 'https://archive.ics.uci.edu/static/public/502/online%2Bretail%2Bii.zip' -OutFile 'data/raw/online_retail_ii_uci.zip'
tar -xf 'data/raw/online_retail_ii_uci.zip' -C 'data/raw'
.\.venv\Scripts\retailmind.exe inspect
.\.venv\Scripts\retailmind.exe prepare
.\.venv\Scripts\retailmind.exe build-snapshot --snapshot validation
.\.venv\Scripts\retailmind.exe build-snapshot --snapshot test
.\.venv\Scripts\retailmind.exe train --snapshot validation
.\.venv\Scripts\retailmind.exe train --snapshot test
.\.venv\Scripts\retailmind.exe analyze-errors --snapshot test
.\.venv\Scripts\ruff.exe check src tests
.\.venv\Scripts\python.exe -m pytest tests -q --basetemp=.pytest_tmp
```

Verify the workbook SHA-256 against the manifest before interpreting the published numbers. The test train command refuses to overwrite a final test report. To rebuild an evaluation after a justified protocol correction, first archive and document the old report and bundles; do not tune from test results.

## Run the API

```powershell
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '4'
.\.venv\Scripts\uvicorn.exe retailmind.api:app --host 127.0.0.1 --port 8000
```

Open the [six-page dashboard](http://127.0.0.1:8000/ui/) or [interactive API docs](http://127.0.0.1:8000/docs). The dashboard uses the real API, including snapshot switching, model comparison, explicit new-customer recommendations, replay with separately revealed outcomes and CSV export. The written design reference is interpreted for this product; no pixel-exact source screen is claimed. To call the API directly:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/health'
Invoke-RestMethod 'http://127.0.0.1:8000/recommendations?customer_id=12384&snapshot=test&k=10'
Invoke-RestMethod 'http://127.0.0.1:8000/recommendations/new?snapshot=test&k=10'
Invoke-RestMethod 'http://127.0.0.1:8000/replay/outcomes?customer_id=12384&snapshot=test'
```

The API also exposes `/snapshots`, `/customers/{id}`, `/products`, `/products/{id}/similar`, `/overview`, `/data-quality`, `/evaluations` and `/evaluations/errors`. `format=csv` works on recommendations and evaluations. Unknown customers return 404; explicit new-customer mode uses Popularity. Invalid query parameters return 422, unknown snapshot 404 and missing model/data 503. Every response has a request ID. The recommendation loader never imports outcome labels; only `/replay/outcomes` reads them.

## Container packaging

After generating local `data/processed` and `artifacts` bundles, `docker compose up --build` starts the API on local port 8000 with read-only mounts for both artifact directories. GitHub Actions has built the image and imported the API. Docker is not installed on the original development machine, so a Compose launch with the real mounted bundles still requires verification on a Docker host. No raw source workbook is copied into the image.

## Verification and performance

A fresh `uv sync --locked --python 3.11 --extra dev` into `.venv_clean` installed 37 packages; 11 fixture tests and Ruff lint passed locally. The 200-request sequential loopback benchmark on Windows 10, CPython 3.11.15, four logical CPUs and one Uvicorn worker measured 32.264 ms p50, 109.029 ms p95, and 2,385.166 ms startup to ready. It used 20 deterministic historical customers, 20 warmups and top-10 recommendations with evidence; it is not a concurrency or UI benchmark. The method and raw summary are in [api_benchmark.json](reports/api_benchmark.json). Rerun with `python scripts/benchmark_api.py` after bundles exist. With the API listening on port 8000, set `$env:RETAILMIND_API_URL = 'http://127.0.0.1:8000'` and run `node scripts/smoke_ui_logic.cjs` to check all six provisional page controllers against real API responses; it is not a visual browser test.

See [release_readiness.md](docs/release_readiness.md), [screenshots](docs/screenshots/), [case_study.md](docs/case_study.md), [demo_script.md](docs/demo_script.md), [api_contract.md](docs/api_contract.md), [architecture.md](docs/architecture.md), [data_dictionary.md](docs/data_dictionary.md), [decisions.md](docs/decisions.md), [progress.md](docs/progress.md), [learning_path.md](docs/learning_path.md) and [code_walkthrough.md](docs/code_walkthrough.md). The UI consumes this API; recommendation logic stays in the service.
