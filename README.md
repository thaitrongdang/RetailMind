# RetailMind

RetailMind ranks up to 10 products for an identified customer at a cutoff, using only earlier transactions to predict purchases in the next 30 days. Repeat purchases are eligible. Model scores are ranking signals, not purchase probabilities.

## Status

The data pipeline, cutoff-safe snapshots, Popularity, ItemCF, ALS, and validation evaluator are implemented. Model selection is being frozen on validation before final test evaluation. The API, final six-page frontend, packaging, and portfolio materials are still in progress. The approved frontend design will be supplied by the project owner.

## Dataset

Source: [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii), DOI 10.24432/C5CG6D, CC BY 4.0. The source workbook is excluded from Git. The verified workbook SHA-256 and actual row counts are in [data_manifest.json](reports/data_manifest.json); cleaning counts are in [data_quality.json](reports/data_quality.json).

The source's timezone is unspecified. RetailMind preserves its timestamp values without assigning UTC. A valid recommendation sale requires an identified customer, positive quantity and price, a usable product code and date, and a non-cancellation invoice. Exact non-merchandise code exclusions are documented in [decisions.md](docs/decisions.md).

## Reproduce the current offline pipeline

Use CPython 3.11 and [uv](https://docs.astral.sh/uv/). In PowerShell:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'
uv sync --python 3.11 --extra dev
New-Item -ItemType Directory -Path data/raw -Force | Out-Null
Invoke-WebRequest -Uri 'https://archive.ics.uci.edu/static/public/502/online%2Bretail%2Bii.zip' -OutFile 'data/raw/online_retail_ii_uci.zip'
tar -xf 'data/raw/online_retail_ii_uci.zip' -C 'data/raw'
.\.venv\Scripts\retailmind.exe inspect
.\.venv\Scripts\retailmind.exe prepare
.\.venv\Scripts\retailmind.exe build-snapshot --snapshot validation
.\.venv\Scripts\retailmind.exe build-snapshot --snapshot test
.\.venv\Scripts\retailmind.exe train --snapshot validation
.\.venv\Scripts\retailmind.exe train --snapshot test
.\.venv\Scripts\python.exe -m pytest tests -q --basetemp=.pytest_tmp
```

Run test training only after reviewing `reports/validation_selection.json`. The test command refuses to overwrite an existing final test report. Raw spreadsheets, full Parquet data, per-customer predictions, and model bundles remain outside Git. Aggregate manifests and evaluation reports are tracked.

## Protocol

- History: timestamps strictly before the cutoff.
- Labels: cutoff inclusive through 30 days later exclusive.
- Candidate set: valid merchandise with identified sales before that cutoff.
- Main evaluation: historical customers with at least one valid future purchase; report empty-label and new-future customers separately.
- Main Recall@10 uses every distinct future product, including products unknown at cutoff. Eligible-label recall and label availability are reported separately.
- All models use the same candidate set and cohort. Validation selects parameters and routing; test uses that frozen choice.
- Validation and test bundles are separate. Outcome labels are stored outside service artifacts.

See [architecture.md](docs/architecture.md), [data_dictionary.md](docs/data_dictionary.md), and [progress.md](docs/progress.md) for implementation details and verified progress.
