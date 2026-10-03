"""Command-line entry point for offline RetailMind workflows."""

import argparse

from retailmind.config import load_config
from retailmind.data.ingest import inspect_workbook, prepare_workbook
from retailmind.data.snapshots import build_snapshot
from retailmind.training import train_test, train_validation


def main() -> None:
    parser = argparse.ArgumentParser(prog="retailmind")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("inspect", help="Inspect source workbook sheets and hash")
    subparsers.add_parser("prepare", help="Build raw and classified Parquet data")
    snapshot_parser = subparsers.add_parser(
        "build-snapshot", help="Build cutoff-safe snapshot and separate outcomes"
    )
    snapshot_parser.add_argument("--snapshot", choices=("validation", "test"), required=True)
    train_parser = subparsers.add_parser(
        "train", help="Search validation or fit frozen models at test cutoff"
    )
    train_parser.add_argument("--snapshot", choices=("validation", "test"), required=True)
    args = parser.parse_args()
    config = load_config()
    if args.command == "inspect":
        inspect_workbook(config)
    elif args.command == "prepare":
        prepare_workbook(config)
    elif args.command == "build-snapshot":
        build_snapshot(config, args.snapshot)
    elif args.command == "train":
        if args.snapshot == "validation":
            train_validation(config)
        else:
            train_test(config)


if __name__ == "__main__":
    main()
