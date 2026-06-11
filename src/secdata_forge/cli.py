from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .drift import detect_drift
from .io import read_table, write_json
from .pipeline import run_pipeline
from .schema import load_config
from .standardize import profile_records, standardize_records
from .validation import validate_baseline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="secdata-forge",
        description="Prepare, score, and compare security datasets.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run the full quality pipeline")
    run.add_argument("--input", required=True, help="CSV, JSON, or JSONL input dataset")
    run.add_argument("--config", required=True, help="JSON config with field and label mappings")
    run.add_argument("--output", required=True, help="Output directory")
    run.add_argument("--reference", help="Optional reference dataset for drift detection")

    profile = subparsers.add_parser("profile", help="Profile a dataset")
    profile.add_argument("--input", required=True)
    profile.add_argument("--config")

    drift = subparsers.add_parser("drift", help="Compare reference and current datasets")
    drift.add_argument("--reference", required=True)
    drift.add_argument("--current", required=True)
    drift.add_argument("--config")
    drift.add_argument("--output", help="Optional JSON output path")

    validate = subparsers.add_parser("validate", help="Run a lightweight downstream baseline")
    validate.add_argument("--input", required=True)
    validate.add_argument("--config", required=True)
    validate.add_argument("--output", help="Optional JSON output path")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        result = run_pipeline(args.input, args.config, args.output, args.reference)
        print(json.dumps(result["paths"], ensure_ascii=False, indent=2))
        return 0
    if args.command == "profile":
        config = load_config(args.config)
        records = standardize_records(read_table(args.input), config)
        print(json.dumps(profile_records(records, config), ensure_ascii=False, indent=2))
        return 0
    if args.command == "drift":
        config = load_config(args.config)
        reference = standardize_records(read_table(args.reference), config)
        current = standardize_records(read_table(args.current), config)
        result = detect_drift(reference, current, config)
        emit(result, args.output)
        return 0
    if args.command == "validate":
        config = load_config(args.config)
        records = standardize_records(read_table(args.input), config)
        result = validate_baseline(records, config)
        emit(result, args.output)
        return 0
    parser.error("Unknown command")
    return 2


def emit(payload: dict[str, Any], output: str | None) -> None:
    if output:
        write_json(Path(output), payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
