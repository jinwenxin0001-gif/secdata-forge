from __future__ import annotations

import json
import unittest
from pathlib import Path

from cyberdata_clean.drift import detect_drift
from cyberdata_clean.io import read_table
from cyberdata_clean.pipeline import run_pipeline
from cyberdata_clean.schema import load_config
from cyberdata_clean.standardize import standardize_records


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "security_flow.json"
CURRENT = ROOT / "examples" / "flows" / "raw_open_security_flows.csv"
REFERENCE = ROOT / "examples" / "flows" / "reference_open_security_flows.csv"


class PipelineTest(unittest.TestCase):
    def test_standardize_normalizes_labels(self) -> None:
        config = load_config(CONFIG)
        records = standardize_records(read_table(CURRENT), config)
        labels = {record["label"] for record in records}
        self.assertIn("benign", labels)
        self.assertIn("ddos", labels)
        self.assertIn("bruteforce", labels)

    def test_pipeline_writes_quality_artifacts(self) -> None:
        output_dir = ROOT / "test_output" / "pipeline"
        output_dir.mkdir(parents=True, exist_ok=True)
        result = run_pipeline(CURRENT, CONFIG, output_dir, REFERENCE)
        paths = result["paths"]
        self.assertTrue(Path(paths["quality_report_json"]).exists())
        self.assertTrue(Path(paths["data_card"]).exists())
        report = json.loads(Path(paths["quality_report_json"]).read_text(encoding="utf-8"))
        self.assertGreater(report["overall_quality_score"], 0.7)
        self.assertGreaterEqual(report["issue_counts"].get("exact_duplicate", 0), 1)

    def test_drift_flags_changed_current_distribution(self) -> None:
        config = load_config(CONFIG)
        reference = standardize_records(read_table(REFERENCE), config)
        current = standardize_records(read_table(CURRENT), config)
        report = detect_drift(reference, current, config)
        self.assertIn(report["summary"]["overall_status"], {"watch", "update_required"})


if __name__ == "__main__":
    unittest.main()
