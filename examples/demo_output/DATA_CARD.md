# Data Card

## Dataset

- Name: `OpenSec-Flow-Demo`
- Task: `intrusion-detection`
- Source: `synthetic-open-security-flow`
- License: `CC0-1.0 demo data`
- Source trust: `0.86`

## Processing Pipeline

1. Source registry and field normalization.
2. Required-field checks, timestamp checks, exact and near-duplicate detection.
3. Label normalization and label-confidence scoring.
4. Sample-level quality scoring and dataset-level quality report.
5. Optional downstream baseline validation and drift detection.

## Quality Snapshot

- Overall quality score: `0.9583`
- High-quality rate: `0.9333`
- Balance score: `0.9467`

## Intended Use

This dataset view is intended for reproducible cybersecurity ML experiments, label auditing, drift monitoring, and high-quality sample selection.

## Limitations

Raw malicious binaries, sensitive payloads, and private traffic should not be published directly. Prefer hashes, metadata, derived features, and documented processing scripts.
