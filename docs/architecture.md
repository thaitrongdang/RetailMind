# Architecture

## Offline path

1. `retailmind inspect` hashes and lists every sheet in the unchanged UCI workbook.
2. `retailmind prepare` streams all rows into lineage-preserving raw Parquet, then DuckDB classifies each row into a mutually exclusive reason. Aggregate reports reconcile with source rows.
3. `retailmind build-snapshot --snapshot validation|test` filters training at `invoice_date < cutoff`. It writes customer RFM, product descriptions and popularity, interactions, analytics sales, and eligible adjustments under a snapshot ID derived from the source and policy.
4. The builder writes future labels in a separate `outcomes/<snapshot_id>` directory. The recommendation model loader does not import the outcome reader.
5. `retailmind train --snapshot validation` compares Popularity, ItemCF, and ALS on the same returning-customer cohort. It selects parameters and routing by NDCG@10, then writes a frozen selection.
6. `retailmind train --snapshot test` checks the frozen evaluation contract, fits new models from test-cutoff history, and evaluates the future window once.

## Serving boundary

Versioned model bundles contain model parameters, mapping hashes, snapshot ID, cutoff, preprocessing policy, and package versions. The service will load only snapshot artifacts and model bundles. Historical replay outcomes will be read by a separate evaluation path. Model scores order items and must not be displayed as purchase probabilities.

## Snapshot and row lineage

`raw_row_id` contains a source hash prefix, sheet index, and original Excel row number. Source workbook and full generated artifacts stay outside Git. Each snapshot has its own manifest and path; validation and test never share a trained model or learned mapping.

## Current implementation status

The offline pipeline and validation model comparison are implemented. FastAPI and the six-page frontend are pending. The frontend design is supplied by the project owner.
