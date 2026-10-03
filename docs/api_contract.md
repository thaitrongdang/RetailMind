# RetailMind V1 API contract

Base URL for local development: `http://127.0.0.1:8000`. OpenAPI is at `/docs` and `/openapi.json`. All routes are read-only GET endpoints. Every response has `X-Request-ID`; JSON bodies include `request_id`. A response with `error` and `request_id` is safe to show in an error state. The HTTP status remains authoritative.

| Route | Parameters | Main purpose |
| --- | --- | --- |
| `/health` | none | 200 when both snapshots and all model bundles are ready; 503 with load error categories otherwise. |
| `/snapshots` | none | Only successfully loaded snapshots, with cutoff, outcome end and counts. |
| `/overview` | `snapshot=test|validation` | Pre-cutoff aggregate KPIs, monthly, country and top-product tables. Includes anonymous sales. |
| `/customers/{customer_id}` | `snapshot`, `history_limit=1..100` | Pre-cutoff customer RFM profile and recent lines. |
| `/recommendations` | `customer_id`, `snapshot`, `k=1..20`, `model=selected|itemcf|als|popularity`, `format=json|csv` | Ranked list for a known historical customer. |
| `/recommendations/new` | `snapshot`, `k=1..20`, `format=json|csv` | Popularity ranking for explicit new-customer mode. |
| `/products` | `snapshot`, optional literal search `q`, `limit=1..100` | Pre-cutoff product search and popularity. |
| `/products/{stock_code}/similar` | `snapshot`, `k=1..20` | ItemCF similarity neighbors from that snapshot. |
| `/evaluations` | `snapshot`, `format=json|csv` | Previously computed offline report, frozen selection and model versions. |
| `/evaluations/errors` | none | Frozen test error analysis only. |
| `/data-quality` | none | Full-source manifest and classification counts; clearly separate from cutoff KPIs. |
| `/replay/outcomes` | `customer_id`, `snapshot` | Observed future labels for a historical customer. This is the sole outcome reader in the API. |

Recommendation response fields: `request_id`, `snapshot_id`, `train_cutoff`, `model_name` (actual routed model), `model_version`, `requested_model`, `customer_id`, `k_requested`, `k_returned`, `mode`, `reason_code`, `score_semantics` and `items`. Each item has `rank`, `stock_code`, `score`, `description_as_of_cutoff`, `repeat_item`, `source_model` and `evidence`. A primary ItemCF or ALS list may fill unused positions from Popularity; inspect `source_model` per item. `score` is model-specific and cannot be compared as a probability or directly across models.

`customer_id=12384&snapshot=test` is a verified example for the local UCI workbook hash recorded in `reports/data_manifest.json`. Validation and test return different `snapshot_id` and `model_version`. The frontend should keep selected snapshot in one state source and replace dependent data together when the user switches it. Cache keys must include at least snapshot ID, model version, customer ID, requested model and k. Never display labels from one snapshot beside recommendations from another.

Errors: invalid query values/missing required values → 422; unknown snapshot or historical customer/product → 404; missing bundle, snapshot artifact or evaluation data → 503. An unknown customer is **not** silently routed to new-customer mode. Use `/recommendations/new` deliberately. A known customer with too little history can receive `mode=fallback` and `reason_code=insufficient_history`. An explicit new customer has `mode=new_customer` and `reason_code=explicit_new_customer`.

CSV recommendations include request/snapshot/cutoff/model/version, routing, score semantics, per-item source and evidence. CSV evaluations include split, model version, horizon, repeat policy, cohort size and metrics. Outcome labels are retrospective purchase observations, not impressions or exposed recommendations. The data-quality route covers the entire source period; label its scope visibly in the UI.