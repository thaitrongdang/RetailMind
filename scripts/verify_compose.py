"""Build and verify Compose with existing real bundles; never retrain models."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from smoke_api import ROOT, require, verify_api


def run(args: list[str]) -> str:
    result = subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(args)}\n{result.stderr[-4000:]}\n{result.stdout[-4000:]}"
        )
    return result.stdout.strip()


def file_hash(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def bundle_hashes() -> dict[str, str]:
    summaries = json.loads(
        (ROOT / "reports/snapshots.json").read_text(encoding="utf-8")
    )
    require(
        set(summaries) == {"test", "validation"}, "Both snapshot summaries are required"
    )
    result = {}
    for summary in summaries.values():
        snapshot_id = summary["snapshot_id"]
        directory = ROOT / "data/processed/snapshots" / snapshot_id
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        require(manifest["snapshot_id"] == snapshot_id, "Snapshot manifest mismatch")
        paths = [directory / "manifest.json"]
        paths.extend(directory / name for name in manifest["service_artifacts"])
        paths.extend(
            ROOT / "data/processed/outcomes" / snapshot_id / name
            for name in manifest["outcome_artifacts"]
        )
        for model in ("popularity", "itemcf", "als"):
            metadata_path = ROOT / "artifacts" / snapshot_id / model / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            require(
                metadata["snapshot_id"] == snapshot_id
                and metadata["train_cutoff"] == manifest["cutoff"],
                "Model belongs to another cutoff",
            )
            paths.append(metadata_path)
            if metadata.get("model_file"):
                paths.append(metadata_path.parent / metadata["model_file"])
        for path in paths:
            result[path.relative_to(ROOT).as_posix()] = file_hash(path)
    return result


def verify(require_clean: bool) -> dict:
    result = {
        "status": "in_progress",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Compose_with_existing_real_snapshot_and_model_bundles",
    }
    compose = [
        "docker",
        "compose",
        "--project-name",
        "retailmind-v1-verification",
        "--file",
        "compose.yaml",
    ]
    started = False
    try:
        git = ["git", "-c", f"safe.directory={ROOT.as_posix()}"]
        result["commit"] = run(git + ["rev-parse", "HEAD"])
        result["working_tree_clean"] = not bool(run(git + ["status", "--porcelain"]))
        if shutil.which("docker") is None:
            result.update(
                status="blocked",
                reason="Docker CLI is unavailable; see docs/docker_setup.md",
            )
            return result
        require(
            not require_clean or result["working_tree_clean"],
            "Release verification requires a clean checkout",
        )
        try:
            version = json.loads(run(["docker", "version", "--format", "{{json .}}"]))
            engine = json.loads(run(["docker", "info", "--format", "{{json .}}"]))
        except RuntimeError as error:
            result.update(
                status="blocked", reason=f"Docker engine is unavailable: {error}"
            )
            return result
        require(
            engine["OSType"] == "linux", "Switch Docker Desktop to Linux containers"
        )
        result["docker"] = {
            "client": version["Client"]["Version"],
            "server": version["Server"]["Version"],
            "os_type": engine["OSType"],
            "compose": run(["docker", "compose", "version", "--short"]),
        }
        before = bundle_hashes()
        serving_paths = run(
            git
            + [
                "ls-files",
                "--",
                "src",
                "configs",
                "reports",
                "ui",
                "pyproject.toml",
                "uv.lock",
                "README.md",
            ]
        ).splitlines()
        serving_hashes = {name: file_hash(ROOT / name) for name in serving_paths}
        config = json.loads(run(compose + ["config", "--format", "json"]))
        mounts = {
            mount["target"]: mount for mount in config["services"]["api"]["volumes"]
        }
        for destination in ("/app/data/processed", "/app/artifacts"):
            require(
                mounts[destination]["read_only"],
                f"{destination}: writable source mount",
            )
            require(
                not mounts[destination].get("bind", {}).get("create_host_path", False),
                f"{destination}: missing sources would be auto-created",
            )
        started = True
        run(
            compose
            + ["up", "--build", "--detach", "--wait", "--wait-timeout", "180", "api"]
        )
        container_id = run(compose + ["ps", "--quiet", "api"])
        require(
            bool(container_id) and "\n" not in container_id,
            "Expected one Compose API container",
        )
        container = json.loads(run(["docker", "inspect", container_id]))[0]
        require(
            container["State"]["Running"]
            and container["State"]["Health"]["Status"] == "healthy",
            "Container is not healthy",
        )
        mounted = {mount["Destination"]: mount for mount in container["Mounts"]}
        for destination in ("/app/data/processed", "/app/artifacts"):
            require(
                not mounted[destination]["RW"], f"Container has writable {destination}"
            )
        port = container["NetworkSettings"]["Ports"]["8000/tcp"]
        require(
            any(
                binding["HostIp"] == "127.0.0.1" and binding["HostPort"] == "8000"
                for binding in port
            ),
            "Expected loopback port 8000 binding",
        )
        # Compare the exact host bundle bytes with the mounted files inside the container.
        probe = "import hashlib,json,pathlib,sys; names=json.loads(sys.argv[1]); print(json.dumps({name:hashlib.sha256(pathlib.Path('/app',name).read_bytes()).hexdigest() for name in names}))"
        mounted_hashes = json.loads(
            run(
                [
                    "docker",
                    "exec",
                    container_id,
                    "/app/.venv/bin/python",
                    "-c",
                    probe,
                    json.dumps(list(before)),
                ]
            )
        )
        require(
            mounted_hashes == before, "Container mounted different snapshot/model bytes"
        )
        image_hashes = json.loads(
            run(
                [
                    "docker",
                    "exec",
                    container_id,
                    "/app/.venv/bin/python",
                    "-c",
                    probe,
                    json.dumps(list(serving_hashes)),
                ]
            )
        )
        require(
            image_hashes == serving_hashes,
            "Container serving files differ from the checked checkout",
        )
        result["api"] = verify_api("http://127.0.0.1:8000")
        require(bundle_hashes() == before, "Serving changed an existing bundle")
        require(
            {name: file_hash(ROOT / name) for name in serving_paths} == serving_hashes,
            "Checkout serving files changed during verification",
        )
        require(
            run(git + ["rev-parse", "HEAD"]) == result["commit"],
            "Checkout commit changed during verification",
        )
        result["working_tree_clean_at_end"] = not bool(
            run(git + ["status", "--porcelain"])
        )
        require(
            not require_clean or result["working_tree_clean_at_end"],
            "Release checkout became dirty during verification",
        )
        result.update(
            status="passed",
            container_id=container_id,
            image_id=container["Image"],
            health=container["State"]["Health"]["Status"],
            read_only_mounts=["/app/data/processed", "/app/artifacts"],
            bundle_sha256=before,
            serving_files_sha256=serving_hashes,
        )
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        result.update(status="failed", reason=str(error))
        if started:
            try:
                result["container_logs"] = run(
                    compose + ["logs", "--no-color", "--tail", "40", "api"]
                )
            except RuntimeError:
                pass
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="Reject dirty checkouts for release verification",
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / ".uv-cache/compose_verification.json"
    )
    args = parser.parse_args()
    result = verify(args.require_clean)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: value
                for key, value in result.items()
                if key
                not in {
                    "bundle_sha256",
                    "serving_files_sha256",
                    "api",
                    "container_logs",
                }
            },
            indent=2,
        )
    )
    print(f"Evidence: {args.output}")
    sys.exit(0 if result["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
