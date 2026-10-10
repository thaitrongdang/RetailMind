"""Package existing bundles for a Docker host and verify the transferred bytes."""

from __future__ import annotations

import argparse
import json
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

from verify_compose import ROOT, bundle_hashes, file_hash, require, run


def checkout_state() -> tuple[str, bool]:
    git = ["git", "-c", f"safe.directory={ROOT.as_posix()}"]
    return run(git + ["rev-parse", "HEAD"]), not bool(
        run(git + ["status", "--porcelain"])
    )


def export(directory: Path, require_clean: bool) -> dict:
    commit, clean = checkout_state()
    require(not require_clean or clean, "Transfer export requires a clean checkout")
    hashes = bundle_hashes()
    # Only files enumerated by the two frozen manifests/models are transferred.
    archive = directory / "retailmind-bundles.tar.gz"
    manifest_path = directory / "transfer_manifest.json"
    require(not archive.exists() and not manifest_path.exists(), "Use a new output directory")
    directory.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "w:gz") as handle:
        for name in sorted(hashes):
            handle.add(ROOT / name, arcname=name, recursive=False)
    require(bundle_hashes() == hashes, "Source bundles changed while packaging")
    manifest = {
        "status": "prepared",
        "scope": "bundle_transfer_only",
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "candidate_commit": commit,
        "source_checkout_clean": clean,
        "archive_name": archive.name,
        "archive_sha256": file_hash(archive),
        "archive_bytes": archive.stat().st_size,
        "bundle_bytes": sum((ROOT / name).stat().st_size for name in hashes),
        "bundle_sha256": hashes,
        "compose_verified": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {key: value for key, value in manifest.items() if key != "bundle_sha256"}


def check(manifest_path: Path, require_clean: bool) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest["schema_version"] == 1, "Unsupported transfer manifest")
    commit, clean = checkout_state()
    require(commit == manifest["candidate_commit"], "Checkout differs from transfer candidate commit")
    require(
        not require_clean or (clean and manifest["source_checkout_clean"]),
        "Verification requires clean source and destination checkouts",
    )
    archive = manifest_path.parent / "retailmind-bundles.tar.gz"
    require(file_hash(archive) == manifest["archive_sha256"], "Archive SHA-256 differs from source")
    actual = bundle_hashes()
    require(actual == manifest["bundle_sha256"], "Transferred bundle bytes differ from source")
    return {
        "status": "passed",
        "scope": "bundle_transfer_only",
        "commit": commit,
        "working_tree_clean": clean,
        "files_checked": len(actual),
        "archive_sha256": manifest["archive_sha256"],
        "compose_verified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    exporter = commands.add_parser("export", help="Archive current real bundles without training")
    exporter.add_argument("--output-dir", type=Path, required=True)
    exporter.add_argument("--require-clean", action="store_true")
    checker = commands.add_parser("check", help="Verify archive and extracted bundles on the destination")
    checker.add_argument("--manifest", type=Path, required=True)
    checker.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    try:
        result = (
            export(args.output_dir, args.require_clean)
            if args.command == "export"
            else check(args.manifest, args.require_clean)
        )
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        print(json.dumps({"status": "failed", "reason": str(error), "compose_verified": False}))
        sys.exit(1)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
