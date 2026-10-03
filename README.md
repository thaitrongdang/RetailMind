# RetailMind

RetailMind is a learning project for customer-level product ranking on historical retail transactions. At a cutoff time, it will rank up to 10 products that an identified customer may buy during the next 30 days. Previously purchased products remain eligible. Ranking scores are not purchase probabilities.

## Current status

Week 1, Session 1 is in progress. This repository currently contains the problem definition, an isolated Python environment setup, a source inspection checklist, and a small teaching example. It does not yet contain the retail dataset, trained models, evaluation results, API, or user interface.

## Dataset and scope

The planned source is [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii), listed as CC BY 4.0 in the project plan. Download and verify its current source details before using it. Source spreadsheets and generated datasets stay outside Git.

An Excel row represents an invoice line. Multiple lines may share an invoice, and a customer may have many invoices. A customer-product interaction aggregates qualifying purchase lines before a cutoff. See [the problem statement](docs/problem_statement.md) for the exact prediction and evaluation boundaries, including a hand-counted cutoff example. Run [the example script](examples/granularity_example.py) to verify its counts.

## Local setup (PowerShell)

Use Python 3.11. The setup performed on this machine was:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'
uv venv .venv --python 3.11 --offline
.\.venv\Scripts\python.exe -c "import sys; print(sys.version)"
.\.venv\Scripts\python.exe examples\granularity_example.py
```

The example uses only the Python standard library. Project dependencies will be added and pinned when the data pipeline begins, after checking compatibility in this environment.

## Next data step

Download the source workbook from UCI into `data/raw/` and follow [the source inspection checklist](docs/source_inspection.md). No full-data counts or cutoff coverage have been verified yet. The `prepare`, `build-snapshot`, `train`, `evaluate`, and `serve` commands in the plan are future interfaces, not commands available in this repository today.

## Project notes

- [Development plan](RetailMind_Codex_Plan.md)
- [Progress checkpoint](docs/progress.md)
- [Learning log](docs/learning_log.md)
- [Decisions](docs/decisions.md)
