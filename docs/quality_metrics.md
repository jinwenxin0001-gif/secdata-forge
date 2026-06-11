# Quality Metrics

The scoring model is deliberately simple. It is not meant to replace domain review, but it gives each release a repeatable first-pass check.

## Record Scores

Each record receives a score in `[0, 1]`.

| Dimension | Meaning |
| --- | --- |
| Provenance | Source trust and traceability. |
| Completeness | Presence of required fields. |
| Label | Whether the source label maps to the configured taxonomy. |
| Uniqueness | Whether the record appears to be duplicated. |
| Freshness | Whether the timestamp is recent enough for the configured use case. |
| Feature | Whether configured numeric features can be parsed. |

Default weights:

```text
score = 0.15 * provenance
      + 0.20 * completeness
      + 0.20 * label
      + 0.15 * uniqueness
      + 0.15 * freshness
      + 0.15 * feature
```

Weights can be changed in the dataset config.

## Dataset Scores

- `overall_quality_score`: mean record score.
- `high_quality_rate`: share of records above the configured threshold.
- `balance_score`: normalized entropy of the label distribution.
- `issue_counts`: counts for missing fields, invalid timestamps, exact duplicates, and near duplicates.
- `drift_report`: PSI and KS for numeric fields; JS divergence for categorical fields.

These metrics are intentionally transparent, so a reviewer can trace a report number back to a field, rule, or record.
