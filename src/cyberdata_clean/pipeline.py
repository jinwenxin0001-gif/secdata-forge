from __future__ import annotations

from pathlib import Path
from typing import Any

from .cleaning import clean_records
from .drift import detect_drift
from .io import ensure_dir, read_table, write_json, write_table
from .quality import score_records
from .report import write_data_card, write_drift_markdown, write_markdown_report
from .schema import load_config
from .standardize import profile_records, standardize_records
from .validation import validate_baseline


def run_pipeline(
    input_path: str | Path,
    config_path: str | Path | None,
    output_dir: str | Path,
    reference_path: str | Path | None = None,
) -> dict[str, Any]:
    config = load_config(config_path)
    output = ensure_dir(output_dir)
    raw_records = read_table(input_path)
    standardized = standardize_records(raw_records, config)
    cleaned, issues = clean_records(standardized, config)
    scored, report = score_records(cleaned, issues, config)
    threshold = float(config.get("quality_threshold", 0.78))
    high_quality = [record for record in scored if float(record.get("_quality_score", 0.0)) >= threshold]
    validation = validate_baseline(high_quality if len(high_quality) >= 6 else scored, config)

    paths = {
        "standardized": str(write_table(output / "standardized.csv", standardized)),
        "cleaned": str(write_table(output / "cleaned.csv", cleaned)),
        "quality_scores": str(write_table(output / "quality_scores.csv", scored)),
        "high_quality": str(write_table(output / "high_quality.csv", high_quality)),
        "issues": str(write_table(output / "issues.csv", issues)),
        "profile": str(write_json(output / "profile.json", profile_records(scored, config))),
        "quality_report_json": str(write_json(output / "quality_report.json", report)),
        "quality_report_md": str(write_markdown_report(output / "quality_report.md", report, validation)),
        "data_card": str(write_data_card(output / "DATA_CARD.md", config, report)),
        "validation_report": str(write_json(output / "validation_report.json", validation)),
    }

    drift_report = None
    if reference_path:
        reference_raw = read_table(reference_path)
        reference = standardize_records(reference_raw, config)
        drift_report = detect_drift(reference, scored, config)
        paths["drift_report_json"] = str(write_json(output / "drift_report.json", drift_report))
        paths["drift_report_md"] = str(write_drift_markdown(output / "drift_report.md", drift_report))

    return {
        "paths": paths,
        "quality_report": report,
        "validation_report": validation,
        "drift_report": drift_report,
    }

