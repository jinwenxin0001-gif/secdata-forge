from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


Record = dict[str, Any]


def ensure_dir(path: str | Path) -> Path:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def read_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str | Path, payload: Any) -> Path:
    target = Path(path)
    ensure_dir(target.parent)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return target


def read_table(path: str | Path) -> list[Record]:
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix == ".csv":
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    if suffix == ".jsonl":
        rows: list[Record] = []
        with source.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    rows.append(json.loads(line))
        return rows
    if suffix == ".json":
        payload = read_json(source)
        if isinstance(payload, list):
            return [dict(row) for row in payload]
        if isinstance(payload, dict) and isinstance(payload.get("records"), list):
            return [dict(row) for row in payload["records"]]
        raise ValueError(f"JSON file {source} must contain a list or a records list")
    raise ValueError(f"Unsupported table format: {source.suffix}")


def write_table(path: str | Path, records: list[Record], fieldnames: list[str] | None = None) -> Path:
    target = Path(path)
    ensure_dir(target.parent)
    suffix = target.suffix.lower()
    if suffix == ".jsonl":
        with target.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
                handle.write("\n")
        return target
    if suffix != ".csv":
        raise ValueError(f"Unsupported output table format: {target.suffix}")
    fields = fieldnames or collect_fieldnames(records)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    return target


def collect_fieldnames(records: list[Record]) -> list[str]:
    seen: set[str] = set()
    fields: list[str] = []
    priority = [
        "sample_id",
        "source",
        "timestamp",
        "task",
        "label",
        "attack_type",
        "_quality_score",
        "_quality_grade",
        "_issues",
    ]
    for field in priority:
        if any(field in record for record in records):
            fields.append(field)
            seen.add(field)
    for record in records:
        for field in record:
            if field not in seen:
                fields.append(field)
                seen.add(field)
    return fields

