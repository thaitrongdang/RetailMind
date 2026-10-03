"""API contract checks without the full UCI workbook or trained bundles."""

from types import SimpleNamespace

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from scipy.sparse import csr_matrix

from retailmind import api
from retailmind.models.catalog import Catalog
from retailmind.models.itemcf import ItemCF
from retailmind.models.popularity import Popularity
from retailmind.service import SnapshotService


def test_api_recommendation_contract_and_failures(tmp_path, monkeypatch):
    products = pd.DataFrame({
        "stock_code": ["A", "B", "C"],
        "description": ["Alpha", "Beta", "Gamma"],
        "popularity_90d": [3, 2, 1],
    })
    customers = pd.DataFrame({
        "customer_id": ["C1", "C2"],
        "frequency_invoices": [2, 1],
    })
    catalog = Catalog(
        "fixture-snapshot", tmp_path, ["C1", "C2"], ["A", "B", "C"],
        products, customers, csr_matrix(np.array([[1, 1, 0], [0, 1, 1]], dtype=np.float32)),
    )
    itemcf = ItemCF(catalog, neighbors=2).fit()
    service = SnapshotService(
        "test",
        {"snapshot_id": "fixture-snapshot", "cutoff": "2011-11-01T00:00:00",
         "outcome_end_exclusive": "2011-12-01T00:00:00", "counts": {}},
        catalog,
        {"itemcf": itemcf, "popularity": Popularity(catalog)},
        {"itemcf": {"model_version": "itemcf-fixture"},
         "popularity": {"model_version": "pop-fixture"}},
        "itemcf", 2,
    )
    monkeypatch.setattr(api, "load_services", lambda _: ({"test": service, "validation": service}, {}))
    config = SimpleNamespace(root=tmp_path, reports_dir=tmp_path, processed_dir=tmp_path,
                             horizon_days=30, k=10)
    with TestClient(api.create_app(config)) as client:
        response = client.get("/recommendations", params={"customer_id": "C1", "k": 3})
        assert response.status_code == 200
        body = response.json()
        assert body["request_id"] == response.headers["X-Request-ID"]
        assert body["model_name"] == "itemcf"
        assert body["snapshot_id"] == "fixture-snapshot"
        assert body["score_semantics"] == "ranking_score_not_purchase_probability"
        assert len({item["stock_code"] for item in body["items"]}) == 3
        assert any(item["repeat_item"] for item in body["items"])
        assert all(item["description_as_of_cutoff"] for item in body["items"])
        assert client.get("/recommendations", params={"customer_id": "C2"}).json()["reason_code"] == "insufficient_history"
        assert client.get("/recommendations/new").json()["reason_code"] == "explicit_new_customer"
        assert client.get("/recommendations", params={"customer_id": "typo"}).status_code == 404
        assert client.get("/recommendations", params={"customer_id": "C1", "k": 0}).status_code == 422
        assert client.get("/recommendations", params={"customer_id": "C1", "snapshot": "wrong"}).status_code == 404
        csv_response = client.get("/recommendations", params={"customer_id": "C1", "format": "csv"})
        assert csv_response.status_code == 200
        assert "model_version" in csv_response.text.splitlines()[0]
        service.models.pop("itemcf")
        unavailable = client.get("/recommendations", params={"customer_id": "C1"})
        assert unavailable.status_code == 503
        assert unavailable.json()["error"] == "model_unavailable"