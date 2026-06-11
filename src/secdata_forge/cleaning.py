from __future__ import annotations

from collections import defaultdict
from typing import Any

from .utils import clean_text, jaccard, parse_datetime, stable_hash, tokens


def clean_records(
    records: list[dict[str, Any]],
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    kept: list[dict[str, Any]] = []
    seen_hashes: dict[str, str] = {}
    text_signatures: list[tuple[str, set[str]]] = []
    required = [str(field) for field in config.get("required_fields", [])]
    identity_fields = [str(field) for field in config.get("identity_fields", [])]
    text_fields = [str(field) for field in config.get("text_fields", [])]
    near_threshold = float(config.get("near_duplicate_threshold", 0.92))
    timestamp_field = str(config.get("timestamp_field", "timestamp"))

    for record in records:
        sample_id = str(record.get("sample_id") or stable_hash(record.values()))
        record_issues: list[str] = []

        missing_fields = [field for field in required if not clean_text(record.get(field))]
        if missing_fields:
            record_issues.append("missing_required")
            issues.append(
                {
                    "sample_id": sample_id,
                    "issue": "missing_required",
                    "severity": "high",
                    "detail": ",".join(missing_fields),
                }
            )

        if record.get(timestamp_field) and parse_datetime(record.get(timestamp_field)) is None:
            record_issues.append("invalid_timestamp")
            issues.append(
                {
                    "sample_id": sample_id,
                    "issue": "invalid_timestamp",
                    "severity": "medium",
                    "detail": str(record.get(timestamp_field)),
                }
            )

        identity = stable_hash([record.get(field, "") for field in identity_fields], length=24)
        if identity in seen_hashes:
            record_issues.append("exact_duplicate")
            issues.append(
                {
                    "sample_id": sample_id,
                    "issue": "exact_duplicate",
                    "severity": "medium",
                    "detail": seen_hashes[identity],
                }
            )
            continue
        seen_hashes[identity] = sample_id

        joined_text = " ".join(clean_text(record.get(field)) for field in text_fields)
        text_tokens = tokens(joined_text)
        if len(text_tokens) >= 5:
            matched_id = _find_near_duplicate(sample_id, text_tokens, text_signatures, near_threshold)
            if matched_id:
                record_issues.append("near_duplicate")
                issues.append(
                    {
                        "sample_id": sample_id,
                        "issue": "near_duplicate",
                        "severity": "low",
                        "detail": matched_id,
                    }
                )
                continue
            text_signatures.append((sample_id, text_tokens))

        enriched = dict(record)
        enriched["_clean_status"] = "review" if record_issues else "accepted"
        enriched["_issues"] = ";".join(record_issues)
        kept.append(enriched)

    return kept, issues


def issue_index(issues: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for issue in issues:
        grouped[str(issue.get("sample_id"))].append(issue)
    return dict(grouped)


def _find_near_duplicate(
    sample_id: str,
    candidate: set[str],
    signatures: list[tuple[str, set[str]]],
    threshold: float,
) -> str | None:
    for previous_id, previous_tokens in signatures:
        if previous_id != sample_id and jaccard(candidate, previous_tokens) >= threshold:
            return previous_id
    return None

