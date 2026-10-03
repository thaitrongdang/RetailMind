"""Small matrix checks for mappings, repeat policy, and bundle integrity."""

import json

import numpy as np
import pandas as pd
import pytest
from scipy.sparse import csr_matrix

from retailmind.models.als import ALS
from retailmind.models.bundle import load_model, save_model
from retailmind.models.catalog import Catalog
from retailmind.models.itemcf import ItemCF
from retailmind.models.popularity import Popularity


def _catalog(tmp_path) -> Catalog:
    snapshot_dir = tmp_path / "snapshot"
    snapshot_dir.mkdir()
    (snapshot_dir / "manifest.json").write_text(
        json.dumps(
            {
                "snapshot_id": "fixture-snapshot",
                "cutoff": "2011-09-01T00:00:00",
                "source_hash": "f" * 64,
                "policy": {"horizon_days": 30, "snapshot_version": "fixture-v1"},
            }
        ),
        encoding="utf-8",
    )
    users = ["C1", "C2"]
    items = ["A", "B", "C"]
    products = pd.DataFrame({"stock_code": items, "popularity_90d": [2, 2, 1]})
    customers = pd.DataFrame({"customer_id": users, "frequency_invoices": [2, 1]})
    counts = csr_matrix(np.array([[2, 1, 0], [0, 1, 1]], dtype=np.float32))
    return Catalog("fixture-snapshot", snapshot_dir, users, items, products, customers, counts)


def test_popularity_and_itemcf_allow_repeats(tmp_path) -> None:
    catalog = _catalog(tmp_path)
    popularity = Popularity(catalog)
    assert popularity.recommend(None, 3)[0]["stock_code"] == "A"
    with pytest.raises(KeyError):
        popularity.recommend("typo", 3)
    model = ItemCF(catalog, neighbors=2, weighting="binary").fit()
    assert model.similarity.diagonal().sum() == 0
    result = model.recommend("C1", 3, with_evidence=True)
    assert len({row["stock_code"] for row in result}) == 3
    assert any(row["repeat_item"] for row in result)
    assert {row["stock_code"] for row in result} == catalog.candidate_set
    assert result[0]["evidence"]["kind"] == "item_similarity_contributions"


def test_als_axis_repeat_and_mapping_hash(tmp_path) -> None:
    catalog = _catalog(tmp_path)
    model = ALS(
        catalog, factors=4, regularization=0.1, iterations=3,
        confidence_scale=2.0, seed=42,
    ).fit()
    assert model.model.user_factors.shape == (2, 4)
    assert model.model.item_factors.shape == (3, 4)
    result = model.recommend("C1", 3, with_evidence=True)
    assert len(result) == 3
    assert {row["stock_code"] for row in result} == {"A", "B", "C"}
    assert any(row["repeat_item"] for row in result)
    artifact_root = tmp_path / "artifacts"
    save_model(
        model, catalog, artifact_root,
        {"factors": 4, "regularization": 0.1, "iterations": 3, "confidence_scale": 2.0, "seed": 42},
    )
    loaded, metadata = load_model(catalog, artifact_root, "als")
    assert metadata["mapping_hashes"] == catalog.mapping_hashes()
    assert loaded.recommend("C1", 3)[0]["stock_code"] in catalog.candidate_set
    catalog.items[0] = "CHANGED"
    with pytest.raises(ValueError, match="mapping"):
        load_model(catalog, artifact_root, "als")
