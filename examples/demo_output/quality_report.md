# Cybersecurity Dataset Quality Report

- Dataset: `OpenSec-Flow-Demo`
- Records after cleaning: **15**
- High-quality records: **14**
- High-quality rate: **0.9333**
- Overall quality score: **0.9583**
- Balance score: **0.9467**

## Label Distribution

| Label | Count |
| --- | ---: |
| benign | 4 |
| botnet | 2 |
| bruteforce | 1 |
| ddos | 2 |
| missing | 1 |
| ransomware | 1 |
| scan | 2 |
| web_attack | 2 |

## Issue Counts

| Issue | Count |
| --- | ---: |
| exact_duplicate | 1 |
| missing_required | 1 |

## Recommendations

- Some required fields are missing; review source registration and field mapping rules.
- Duplicate or near-duplicate records were found; keep the issue list with the release.

## Downstream Baseline Validation

- Status: `ok`
- accuracy: **1.0**
- macro_precision: **1.0**
- macro_recall: **1.0**
- macro_f1: **1.0**
