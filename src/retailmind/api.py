"""FastAPI read API for historical, cutoff-safe RetailMind bundles."""

from __future__ import annotations

import csv
import io
import json
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Literal

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from retailmind.config import ProjectConfig, load_config
from retailmind.service import ServiceUnavailable, SnapshotService, load_services


class RecommendationItem(BaseModel):
    rank: int
    stock_code: str
    score: float
    description_as_of_cutoff: str
    repeat_item: bool
    source_model: str
    evidence: dict[str, Any] | None


class RecommendationResponse(BaseModel):
    request_id: str
    snapshot_id: str
    train_cutoff: str
    model_name: str
    model_version: str
    requested_model: str
    customer_id: str | None
    k_requested: int
    k_returned: int
    mode: str
    reason_code: str
    score_semantics: str
    items: list[RecommendationItem]


def _csv(data: dict[str, Any], rows: list[dict[str, Any]], fields: list[str]) -> Response:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: json.dumps(value) if isinstance(value, (list, dict)) else value for key, value in row.items()})
    return Response(stream.getvalue(), media_type="text/csv; charset=utf-8", headers={
        "Content-Disposition": "attachment; filename=retailmind-export.csv",
        "X-RetailMind-Snapshot-ID": str(data.get("snapshot_id", "")),
    })


def create_app(config: ProjectConfig | None = None) -> FastAPI:
    config = config or load_config()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.services, app.state.load_errors = load_services(config)
        yield
        app.state.services.clear()

    app = FastAPI(title="RetailMind API", version="1.0.0", lifespan=lifespan)

    @app.middleware("http")
    async def request_log(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            request.state.error = type(exc).__name__
            response = JSONResponse(status_code=503, content={
                "error": "service_error", "request_id": request_id,
            })
        response.headers["X-Request-ID"] = request_id
        record = {
            "request_id": request_id, "path": request.url.path,
            "snapshot": request.query_params.get("snapshot"),
            "status": response.status_code,
            "latency_ms": round((time.perf_counter() - started) * 1000, 3),
            "mode": getattr(request.state, "mode", None),
            "result_count": getattr(request.state, "result_count", None),
            "error": getattr(request.state, "error", None),
        }
        log_dir = config.root / "logs"
        try:
            log_dir.mkdir(exist_ok=True)
            with (log_dir / "api.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except OSError:
            pass
        return response

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        request.state.error = exc.detail
        return JSONResponse(status_code=exc.status_code, content={
            "error": exc.detail, "request_id": request.state.request_id,
        })

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        request.state.error = "invalid_request"
        return JSONResponse(status_code=422, content={
            "error": "invalid_request", "details": exc.errors(),
            "request_id": request.state.request_id,
        })

    def get_snapshot(request: Request, name: str) -> SnapshotService:
        if name not in ("validation", "test"):
            raise HTTPException(404, "snapshot_not_found")
        service = request.app.state.services.get(name)
        if service is None:
            raise HTTPException(503, "snapshot_or_model_unavailable")
        return service

    @app.get("/health")
    def health(request: Request):
        services = request.app.state.services
        errors = request.app.state.load_errors
        ready = len(services) == 2 and not errors
        return JSONResponse(status_code=200 if ready else 503, content={
            "status": "ready" if ready else "degraded",
            "loaded_snapshots": sorted(services), "load_errors": errors,
            "request_id": request.state.request_id,
        })

    @app.get("/snapshots")
    def snapshots(request: Request):
        return {"request_id": request.state.request_id, "snapshots": [
            {"name": name, "snapshot_id": service.snapshot_id,
             "train_cutoff": service.manifest["cutoff"],
             "outcome_end_exclusive": service.manifest["outcome_end_exclusive"],
             "counts": service.manifest["counts"],
             "available_models": sorted(service.models)}
            for name, service in sorted(request.app.state.services.items())
        ]}

    @app.get("/customers/{customer_id}")
    def customer(request: Request, customer_id: str, snapshot: str = "test", history_limit: int = Query(25, ge=1, le=100)):
        service = get_snapshot(request, snapshot)
        try:
            return {"request_id": request.state.request_id, **service.customer(customer_id, history_limit)}
        except KeyError:
            raise HTTPException(404, "customer_not_found") from None

    @app.get("/recommendations", response_model=RecommendationResponse)
    def recommendations(request: Request, customer_id: str, snapshot: str = "test", k: int = Query(10, ge=1, le=20), model: Literal["selected", "itemcf", "als", "popularity"] = "selected", format: Literal["json", "csv"] = "json"):
        service = get_snapshot(request, snapshot)
        try:
            result = service.recommend(customer_id, k, model)
        except KeyError:
            raise HTTPException(404, "customer_not_found") from None
        except ServiceUnavailable:
            raise HTTPException(503, "model_unavailable") from None
        request.state.mode = result["mode"]
        request.state.result_count = result["k_returned"]
        result["request_id"] = request.state.request_id
        if format == "csv":
            return _csv(result, [{**{key: value for key, value in result.items() if key != "items"}, **row} for row in result["items"]], [
                "request_id", "snapshot_id", "train_cutoff", "model_name", "model_version", "requested_model", "customer_id", "k_requested", "k_returned", "mode", "reason_code", "score_semantics", "rank", "stock_code", "score", "description_as_of_cutoff", "repeat_item", "source_model", "evidence",
            ])
        return result

    @app.get("/recommendations/new", response_model=RecommendationResponse)
    def new_customer(request: Request, snapshot: str = "test", k: int = Query(10, ge=1, le=20), format: Literal["json", "csv"] = "json"):
        service = get_snapshot(request, snapshot)
        try:
            result = service.recommend(None, k)
        except ServiceUnavailable:
            raise HTTPException(503, "model_unavailable") from None
        request.state.mode = result["mode"]
        request.state.result_count = result["k_returned"]
        result["request_id"] = request.state.request_id
        if format == "csv":
            return _csv(result, [{**{key: value for key, value in result.items() if key != "items"}, **row} for row in result["items"]], [
                "request_id", "snapshot_id", "train_cutoff", "model_name", "model_version", "requested_model", "customer_id", "k_requested", "k_returned", "mode", "reason_code", "score_semantics", "rank", "stock_code", "score", "description_as_of_cutoff", "repeat_item", "source_model", "evidence",
            ])
        return result

    @app.get("/products")
    def products(request: Request, snapshot: str = "test", q: str | None = Query(None, max_length=80), limit: int = Query(25, ge=1, le=100)):
        service = get_snapshot(request, snapshot)
        return {"request_id": request.state.request_id, **service.products(q, limit)}

    @app.get("/products/{stock_code}/similar")
    def similar(request: Request, stock_code: str, snapshot: str = "test", k: int = Query(10, ge=1, le=20)):
        service = get_snapshot(request, snapshot)
        try:
            return {"request_id": request.state.request_id, **service.similar(stock_code, k)}
        except KeyError:
            raise HTTPException(404, "product_not_found") from None
        except ServiceUnavailable:
            raise HTTPException(503, "model_unavailable") from None

    @app.get("/evaluations")
    def evaluations(request: Request, snapshot: str = "test", format: Literal["json", "csv"] = "json"):
        service = get_snapshot(request, snapshot)
        filename = "validation_selection.json" if snapshot == "validation" else "test_metrics.json"
        path = config.reports_dir / filename
        if not path.is_file():
            raise HTTPException(503, "evaluation_unavailable")
        report = json.loads(path.read_text(encoding="utf-8"))
        metrics = report.get("model_metrics", report.get("best_model_metrics", {}))
        result = {"request_id": request.state.request_id, "snapshot_id": service.snapshot_id,
                  "train_cutoff": service.manifest["cutoff"], "split": snapshot,
                  "selected_model": report["selected_model"], "model_versions": {
                      name: meta["model_version"] for name, meta in service.metadata.items()},
                  "evaluation_contract": report.get("evaluation_contract") or json.loads((config.reports_dir / "validation_selection.json").read_text(encoding="utf-8"))["evaluation_contract"],
                  "model_metrics": metrics,
                  "selected_routed_metrics": report["selected_routed_metrics"]}
        if format == "csv":
            rows = [{"request_id": request.state.request_id, "snapshot_id": service.snapshot_id,
                     "train_cutoff": service.manifest["cutoff"], "split": snapshot,
                     "model_name": name, "model_version": service.metadata.get(name, {}).get("model_version"),
                     "repeat_purchase_policy": "allowed", "horizon_days": config.horizon_days,
                     "k": config.k, "evaluated_customers": values.get("evaluated_customers"),
                     "recall_at_10": values.get("recall_at_10"), "ndcg_at_10": values.get("ndcg_at_10"),
                     "hit_rate_at_10": values.get("hit_rate_at_10")}
                    for name, values in metrics.items()]
            return _csv(result, rows, list(rows[0]) if rows else [])
        return result

    @app.get("/replay/outcomes")
    def outcomes(request: Request, customer_id: str, snapshot: str = "test"):
        service = get_snapshot(request, snapshot)
        if customer_id not in service.catalog.user_index:
            raise HTTPException(404, "customer_not_found")
        path = config.processed_dir / "outcomes" / service.snapshot_id / "labels.parquet"
        if not path.is_file():
            raise HTTPException(503, "outcomes_unavailable")
        labels = pd.read_parquet(path, filters=[("customer_id", "==", customer_id)])
        return {"request_id": request.state.request_id, "snapshot_id": service.snapshot_id,
                "outcome_start": service.manifest["cutoff"],
                "outcome_end_exclusive": service.manifest["outcome_end_exclusive"],
                "customer_id": customer_id,
                "labels": json.loads(labels.to_json(orient="records", date_format="iso"))}

    @app.get("/overview")
    def overview(request: Request, snapshot: str = "test"):
        from retailmind.analytics import overview as build_overview

        service = get_snapshot(request, snapshot)
        return {"request_id": request.state.request_id, **build_overview(service)}

    @app.get("/data-quality")
    def data_quality(request: Request):
        quality_path = config.reports_dir / "data_quality.json"
        manifest_path = config.reports_dir / "data_manifest.json"
        if not quality_path.is_file() or not manifest_path.is_file():
            raise HTTPException(503, "data_quality_unavailable")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return {
            "request_id": request.state.request_id,
            "scope": "full_source_all_dates_not_cutoff_snapshot",
            "source_hash": manifest["workbook_sha256"],
            "license": manifest["license"],
            "sheets": manifest["sheets"],
            "excluded_stock_codes": manifest["excluded_stock_codes"],
            "quality": json.loads(quality_path.read_text(encoding="utf-8")),
        }

    @app.get("/evaluations/errors")
    def evaluation_errors(request: Request):
        path = config.reports_dir / "test_error_analysis.json"
        if not path.is_file():
            raise HTTPException(503, "error_analysis_unavailable")
        return {"request_id": request.state.request_id,
                "split": "test", "analysis": json.loads(path.read_text(encoding="utf-8"))}
    return app


app = create_app()