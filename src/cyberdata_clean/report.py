from __future__ import annotations

from pathlib import Path
from typing import Any

from .io import ensure_dir


def write_markdown_report(path: str | Path, report: dict[str, Any], validation: dict[str, Any] | None = None) -> Path:
    target = Path(path)
    ensure_dir(target.parent)
    lines = [
        "# Cybersecurity Dataset Quality Report",
        "",
        f"- Dataset: `{report.get('dataset')}`",
        f"- Records after cleaning: **{report.get('records_after_cleaning', 0)}**",
        f"- High-quality records: **{report.get('high_quality_records', 0)}**",
        f"- High-quality rate: **{report.get('high_quality_rate', 0)}**",
        f"- Overall quality score: **{report.get('overall_quality_score', 0)}**",
        f"- Balance score: **{report.get('balance_score', 0)}**",
        "",
        "## Label Distribution",
        "",
        "| Label | Count |",
        "| --- | ---: |",
    ]
    for label, count in sorted(report.get("label_distribution", {}).items()):
        lines.append(f"| {label} | {count} |")
    lines.extend(["", "## Issue Counts", "", "| Issue | Count |", "| --- | ---: |"])
    for issue, count in sorted(report.get("issue_counts", {}).items()):
        lines.append(f"| {issue} | {count} |")
    lines.extend(["", "## Recommendations", ""])
    for item in report.get("recommendations", []):
        lines.append(f"- {item}")
    if validation:
        lines.extend(["", "## Downstream Baseline Validation", ""])
        lines.append(f"- Status: `{validation.get('status')}`")
        if validation.get("metrics"):
            for key, value in validation["metrics"].items():
                lines.append(f"- {key}: **{value}**")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def write_data_card(path: str | Path, config: dict[str, Any], report: dict[str, Any]) -> Path:
    target = Path(path)
    ensure_dir(target.parent)
    dataset = config.get("dataset", {})
    lines = [
        "# Data Card",
        "",
        f"## Dataset",
        "",
        f"- Name: `{dataset.get('name', 'unknown')}`",
        f"- Task: `{dataset.get('task', 'unknown')}`",
        f"- Source: `{dataset.get('source', 'unknown')}`",
        f"- License: `{dataset.get('license', 'unknown')}`",
        f"- Source trust: `{dataset.get('source_trust', 'unknown')}`",
        "",
        "## Processing Pipeline",
        "",
        "1. Source registry and field normalization.",
        "2. Required-field checks, timestamp checks, exact and near-duplicate detection.",
        "3. Label normalization and label-confidence scoring.",
        "4. Sample-level quality scoring and dataset-level quality report.",
        "5. Optional downstream baseline validation and drift detection.",
        "",
        "## Quality Snapshot",
        "",
        f"- Overall quality score: `{report.get('overall_quality_score')}`",
        f"- High-quality rate: `{report.get('high_quality_rate')}`",
        f"- Balance score: `{report.get('balance_score')}`",
        "",
        "## Intended Use",
        "",
        "This dataset view is intended for reproducible cybersecurity ML experiments, label auditing, drift monitoring, and high-quality sample selection.",
        "",
        "## Limitations",
        "",
        "Raw malicious binaries, sensitive payloads, and private traffic should not be published directly. Prefer hashes, metadata, derived features, and documented processing scripts.",
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def write_drift_markdown(path: str | Path, drift: dict[str, Any]) -> Path:
    target = Path(path)
    ensure_dir(target.parent)
    lines = [
        "# Drift Report",
        "",
        f"- Overall status: **{drift.get('summary', {}).get('overall_status')}**",
        f"- Features checked: **{drift.get('summary', {}).get('features_checked', 0)}**",
        "",
        "## Numeric Drift",
        "",
        "| Feature | PSI | KS | Severity |",
        "| --- | ---: | ---: | --- |",
    ]
    for item in drift.get("numeric_drift", []):
        lines.append(f"| {item['feature']} | {item['psi']} | {item['ks']} | {item['severity']} |")
    lines.extend(["", "## Categorical Drift", "", "| Feature | JS Divergence | Severity |", "| --- | ---: | --- |"])
    for item in drift.get("categorical_drift", []):
        lines.append(f"| {item['feature']} | {item['js_divergence']} | {item['severity']} |")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target

