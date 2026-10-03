"""Versioned, cutoff-bound model bundles with mapping checks."""

from __future__ import annotations

import hashlib
import json
from importlib.metadata import version
from pathlib import Path
from typing import Any

from retailmind.models.als import ALS
from retailmind.models.catalog import Catalog
from retailmind.models.itemcf import ItemCF
from retailmind.models.popularity import Popularity


def bundle_directory(artifact_root: Path, catalog: Catalog, model_name: str) -> Path:
    return artifact_root / catalog.snapshot_id / model_name


def save_model(
    model: Popularity | ItemCF | ALS,
    catalog: Catalog,
    artifact_root: Path,
    params: dict[str, Any],
) -> dict[str, Any]:
    snapshot_manifest = json.loads(
        (catalog.snapshot_dir / "manifest.json").read_text(encoding="utf-8")
    )
    mapping_hashes = catalog.mapping_hashes()
    identity = {
        "snapshot_id": catalog.snapshot_id,
        "model_name": model.name,
        "params": params,
        "mapping_hashes": mapping_hashes,
    }
    model_version = hashlib.sha256(
        json.dumps(identity, sort_keys=True).encode()
    ).hexdigest()[:16]
    directory = bundle_directory(artifact_root, catalog, model.name)
    directory.mkdir(parents=True, exist_ok=True)
    model_file = None
    if isinstance(model, ItemCF):
        model_file = "similarity.npz"
        model.save(directory / model_file)
    elif isinstance(model, ALS):
        model_file = "als_model.npz"
        model.save(directory / model_file)
    metadata = {
        **identity,
        "model_version": model_version,
        "model_file": model_file,
        "train_cutoff": snapshot_manifest["cutoff"],
        "label_horizon_days": snapshot_manifest["policy"]["horizon_days"],
        "candidate_policy": "identified_valid_merchandise_sales_before_cutoff",
        "repeat_purchase_policy": "allowed",
        "preprocessing_version": snapshot_manifest["policy"]["snapshot_version"],
        "source_hash": snapshot_manifest["source_hash"],
        "package_versions": {
            package: version(package)
            for package in ("numpy", "scipy", "implicit", "duckdb")
        },
    }
    (directory / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return metadata


def load_model(
    catalog: Catalog, artifact_root: Path, model_name: str
) -> tuple[Popularity | ItemCF | ALS, dict[str, Any]]:
    directory = bundle_directory(artifact_root, catalog, model_name)
    metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
    if metadata["snapshot_id"] != catalog.snapshot_id:
        raise ValueError("Bundle snapshot ID does not match service snapshot")
    if metadata["mapping_hashes"] != catalog.mapping_hashes():
        raise ValueError("Bundle user/item mapping differs from snapshot")
    params = metadata["params"]
    if model_name == "popularity":
        model = Popularity(catalog)
    elif model_name == "itemcf":
        model = ItemCF.load(
            catalog, directory / metadata["model_file"], params["neighbors"], params["weighting"]
        )
    elif model_name == "als":
        model = ALS.load(
            catalog,
            directory / metadata["model_file"],
            params["factors"],
            params["regularization"],
            params["iterations"],
            params["confidence_scale"],
            params["seed"],
        )
    else:
        raise ValueError(f"Unknown model: {model_name}")
    return model, metadata
