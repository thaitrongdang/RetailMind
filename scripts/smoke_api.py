"""Check a running API against the real, already frozen local bundle reports."""

from __future__ import annotations

import argparse
import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verify_api(base_url: str, root: Path = ROOT) -> dict:
    """Verify HTTP behavior without training models or modifying frozen reports."""
    base_url = base_url.rstrip("/")
    snapshots = json.loads(
        (root / "reports/snapshots.json").read_text(encoding="utf-8")
    )
    checks: list[str] = []

    def request(path: str, expected: int = 200) -> tuple[dict, bytes]:
        try:
            response = urlopen(base_url + path, timeout=30)
        except HTTPError as error:
            response = error
        with response:
            body = response.read()
            require(
                response.status == expected,
                f"{path}: HTTP {response.status}, expected {expected}",
            )
            headers = {key.lower(): value for key, value in response.headers.items()}
            require(
                bool(response.headers.get("X-Request-ID")),
                f"{path}: missing request ID",
            )
        checks.append(f"{path}: HTTP {expected}")
        return headers, body

    def get(path: str, expected: int = 200) -> dict:
        headers, body = request(path, expected)
        data = json.loads(body)
        require(
            data.get("request_id") == headers.get("x-request-id"),
            f"{path}: request ID mismatch",
        )
        return data

    health = get("/health")
    require(
        health["status"] == "ready"
        and health["loaded_snapshots"] == ["test", "validation"],
        "Both bundles must be ready",
    )
    require(not health["load_errors"], "Bundle loading reported errors")
    _, html = request("/ui/")
    require(b"RetailMind" in html, "Dashboard HTML missing")
    for asset in ("app.js", "style.css", "favicon.svg"):
        request("/ui/" + asset)
    available = {item["name"]: item for item in get("/snapshots")["snapshots"]}
    require(set(available) == {"validation", "test"}, "Snapshot listing is incomplete")
    details = {}
    for name, summary in sorted(snapshots.items()):
        listed = available[name]
        require(
            listed["snapshot_id"] == summary["snapshot_id"],
            f"{name}: snapshot ID mismatch",
        )
        require(listed["train_cutoff"] == summary["cutoff"], f"{name}: cutoff mismatch")
        require(
            listed["counts"] == summary["counts"], f"{name}: real-data counts mismatch"
        )
        require(
            listed["available_models"] == ["als", "itemcf", "popularity"],
            f"{name}: missing model",
        )
        query = urlencode({"customer_id": "12384", "snapshot": name, "k": 10})
        profile = get(f"/customers/12384?snapshot={name}")
        cutoff = datetime.fromisoformat(summary["cutoff"])
        require(
            all(
                datetime.fromisoformat(row["invoice_date"]) < cutoff
                for row in profile["recent_lines"]
            ),
            f"{name}: future history exposed",
        )
        recommendations = {}
        for model in ("selected", "popularity", "itemcf", "als"):
            ranking = get(f"/recommendations?{query}&model={model}")
            require(
                ranking["snapshot_id"] == summary["snapshot_id"],
                f"{name}/{model}: snapshot mismatch",
            )
            require(
                ranking["train_cutoff"] == summary["cutoff"],
                f"{name}/{model}: cutoff mismatch",
            )
            require(
                ranking["k_returned"] == len(ranking["items"]) == 10,
                f"{name}/{model}: expected ten items",
            )
            codes = [item["stock_code"] for item in ranking["items"]]
            require(len(set(codes)) == 10, f"{name}/{model}: duplicate recommendations")
            require(
                [item["rank"] for item in ranking["items"]] == list(range(1, 11)),
                f"{name}/{model}: rank order invalid",
            )
            require(
                all(
                    item["source_model"] in {ranking["model_name"], "popularity"}
                    for item in ranking["items"]
                ),
                f"{name}/{model}: invalid per-item model source",
            )
            require(
                ranking["score_semantics"] == "ranking_score_not_purchase_probability",
                "Incorrect score semantics",
            )
            metadata = json.loads(
                (
                    root
                    / "artifacts"
                    / summary["snapshot_id"]
                    / ranking["model_name"]
                    / "metadata.json"
                ).read_text(encoding="utf-8")
            )
            require(
                ranking["model_version"] == metadata["model_version"],
                f"{name}/{model}: wrong mounted model version",
            )
            recommendations[model] = ranking
        fresh = get(f"/recommendations/new?snapshot={name}&k=10")
        require(
            fresh["model_name"] == "popularity" and fresh["customer_id"] is None,
            "New-customer mode must use Popularity",
        )
        require(
            fresh["reason_code"] == "explicit_new_customer",
            "Missing explicit new-customer reason",
        )
        headers, content = request(f"/recommendations?{query}&format=csv")
        rows = list(csv.DictReader(io.StringIO(content.decode("utf-8"))))
        require(
            len(rows) == 10
            and all(row["snapshot_id"] == summary["snapshot_id"] for row in rows),
            "CSV lost snapshot metadata",
        )
        require(
            headers.get("x-retailmind-snapshot-id") == summary["snapshot_id"],
            "CSV snapshot header mismatch",
        )
        labels = get(f"/replay/outcomes?customer_id=12384&snapshot={name}")
        end = datetime.fromisoformat(summary["outcome_end_exclusive"])
        require(
            all(
                cutoff <= datetime.fromisoformat(row["first_outcome_time"]) < end
                for row in labels["labels"]
            ),
            "Outcome timestamp outside its window",
        )
        after = get(f"/recommendations?{query}&model=selected")
        require(
            after["items"] == recommendations["selected"]["items"],
            "Ranking changed after reading outcomes",
        )
        report_name = (
            "validation_selection.json" if name == "validation" else "test_metrics.json"
        )
        frozen = json.loads(
            (root / "reports" / report_name).read_text(encoding="utf-8")
        )
        evaluation = get(f"/evaluations?snapshot={name}")
        require(
            evaluation["model_metrics"]
            == frozen.get("model_metrics", frozen.get("best_model_metrics")),
            "API metrics differ from frozen report",
        )
        require(
            evaluation["selected_model"] == frozen["selected_model"],
            "API model selection differs from validation choice",
        )
        require(
            recommendations["selected"]["model_name"] == frozen["selected_model"],
            "Selected serving model differs from frozen choice",
        )
        require(
            get(f"/overview?snapshot={name}")["snapshot_id"] == summary["snapshot_id"],
            "Overview lost snapshot context",
        )
        products = get(f"/products?snapshot={name}&limit=10")
        require(
            products["snapshot_id"] == summary["snapshot_id"] and products["items"],
            "Product listing missing",
        )
        code = products["items"][0]["stock_code"]
        neighbors = get(f"/products/{code}/similar?snapshot={name}")
        require(
            all(item["stock_code"] != code for item in neighbors["items"]),
            "ItemCF returned self similarity",
        )
        details[name] = {
            "snapshot_id": summary["snapshot_id"],
            "counts": summary["counts"],
            "models": {
                model: {
                    "model_version": ranking["model_version"],
                    "stock_codes": [item["stock_code"] for item in ranking["items"]],
                }
                for model, ranking in recommendations.items()
            },
            "outcomes_observed": len(labels["labels"]),
        }
    quality = get("/data-quality")
    manifest = json.loads(
        (root / "reports/data_manifest.json").read_text(encoding="utf-8")
    )
    require(
        quality["source_hash"] == manifest["workbook_sha256"],
        "API uses a different source workbook",
    )
    require(
        quality["quality"]
        == json.loads((root / "reports/data_quality.json").read_text(encoding="utf-8")),
        "API quality report differs from checkout",
    )
    get("/evaluations/errors")
    for path, status, error in (
        (
            "/recommendations?customer_id=unknown-id&snapshot=test",
            404,
            "customer_not_found",
        ),
        (
            "/recommendations?customer_id=12384&snapshot=unknown",
            404,
            "snapshot_not_found",
        ),
        ("/recommendations?customer_id=12384&k=0", 422, "invalid_request"),
        ("/recommendations?customer_id=12384&k=11", 422, "invalid_request"),
        ("/recommendations/new?k=11", 422, "invalid_request"),
    ):
        require(get(path, status)["error"] == error, f"{path}: wrong failure reason")
    return {
        "status": "passed",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "checks": checks,
        "snapshots": details,
        "scope": "real_bundle_HTTP_check_not_a_container_or_browser_claim",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify_api(args.base_url)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "base_url": result["base_url"],
                "HTTP_checks": len(result["checks"]),
                "snapshots": {
                    name: value["snapshot_id"]
                    for name, value in result["snapshots"].items()
                },
                "output": str(args.output) if args.output else None,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
