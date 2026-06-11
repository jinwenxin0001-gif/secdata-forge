from __future__ import annotations

from pathlib import Path
from typing import Any

from .io import read_json


DEFAULT_CONFIG: dict[str, Any] = {
    "dataset": {
        "name": "open-security-dataset",
        "task": "intrusion-detection",
        "source": "unknown",
        "source_trust": 0.7,
        "license": "unknown",
    },
    "field_mapping": {},
    "label_mapping": {
        "benign": "benign",
        "normal": "benign",
        "attack": "attack",
        "malicious": "malicious",
    },
    "required_fields": ["timestamp", "label"],
    "identity_fields": ["timestamp", "src_ip", "dst_ip", "protocol", "label", "attack_type"],
    "numeric_features": [],
    "categorical_features": ["protocol", "label", "attack_type"],
    "text_fields": ["text", "description", "message"],
    "quality_threshold": 0.78,
    "quality_weights": {
        "provenance": 0.15,
        "completeness": 0.20,
        "label": 0.20,
        "uniqueness": 0.15,
        "freshness": 0.15,
        "feature": 0.15,
    },
    "near_duplicate_threshold": 0.92,
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return dict(DEFAULT_CONFIG)
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise ValueError("Configuration must be a JSON object")
    return deep_merge(DEFAULT_CONFIG, payload)


def label_field(config: dict[str, Any]) -> str:
    return str(config.get("label_field") or "label")


def timestamp_field(config: dict[str, Any]) -> str:
    return str(config.get("timestamp_field") or "timestamp")

