from __future__ import annotations

from typing import Any

from .utils import clean_text, normalize_key, stable_hash


def standardize_records(records: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    return [standardize_record(record, config, index) for index, record in enumerate(records, start=1)]


def standardize_record(record: dict[str, Any], config: dict[str, Any], index: int) -> dict[str, Any]:
    mapping = {str(key): str(value) for key, value in config.get("field_mapping", {}).items()}
    label_map = {normalize_key(key): str(value) for key, value in config.get("label_mapping", {}).items()}
    dataset = config.get("dataset", {})

    normalized: dict[str, Any] = {}
    for raw_key, value in record.items():
        canonical_key = mapping.get(raw_key, mapping.get(normalize_key(raw_key), normalize_key(raw_key)))
        normalized[canonical_key] = clean_text(value)

    original_label = normalized.get("label", "")
    if original_label:
        normalized["_original_label"] = original_label
        normalized["label"] = label_map.get(normalize_key(original_label), normalize_key(original_label))

    if not normalized.get("source"):
        normalized["source"] = dataset.get("source") or dataset.get("name") or "unknown"
    if not normalized.get("task"):
        normalized["task"] = dataset.get("task", "unknown")
    normalized["_source_trust"] = str(dataset.get("source_trust", 0.7))
    normalized["_license"] = dataset.get("license", "unknown")

    identity_fields = config.get("identity_fields") or ["timestamp", "label"]
    if not normalized.get("sample_id"):
        identity_values = [normalized.get(field, "") for field in identity_fields]
        normalized["sample_id"] = stable_hash([index, *identity_values])

    return normalized


def profile_records(records: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    total = len(records)
    fields: dict[str, int] = {}
    labels: dict[str, int] = {}
    label_name = config.get("label_field", "label")
    for record in records:
        for key, value in record.items():
            if value not in (None, ""):
                fields[key] = fields.get(key, 0) + 1
        label = str(record.get(label_name, "") or "missing")
        labels[label] = labels.get(label, 0) + 1
    return {
        "records": total,
        "field_coverage": {key: round(value / total, 4) if total else 0.0 for key, value in fields.items()},
        "label_distribution": labels,
    }

