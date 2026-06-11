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

- 存在关键字段缺失样本，建议完善来源登记和字段映射规则。
- 检测到重复或近重复样本，建议在版本发布前保留去重清单。

## Downstream Baseline Validation

- Status: `ok`
- accuracy: **1.0**
- macro_precision: **1.0**
- macro_recall: **1.0**
- macro_f1: **1.0**
