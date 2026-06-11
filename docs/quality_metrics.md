# Quality Metrics

The scoring model is intentionally transparent. Each sample receives a score in `[0, 1]`, then the dataset receives aggregate metrics.

## Sample-Level Dimensions

| Dimension | Meaning |
| --- | --- |
| Provenance | Whether the source is trusted and documented. |
| Completeness | Whether required fields are present. |
| Label | Whether the label can be normalized to the configured taxonomy. |
| Uniqueness | Whether the sample is free from exact or near duplication. |
| Freshness | Whether the timestamp is recent enough for current threat modeling. |
| Feature | Whether configured numeric features are usable. |

The default weighted score is:

```text
score = 0.15 * provenance
      + 0.20 * completeness
      + 0.20 * label
      + 0.15 * uniqueness
      + 0.15 * freshness
      + 0.15 * feature
```

## Dataset-Level Metrics

- `overall_quality_score`: mean sample quality score.
- `high_quality_rate`: percentage of samples above the configured quality threshold.
- `balance_score`: normalized entropy of label distribution.
- `issue_counts`: missing fields, invalid timestamps, exact duplicates, near duplicates.
- `drift_report`: PSI/KS for numeric features and JS divergence for categorical features.

These metrics map directly to the proposal dimensions: authenticity, accuracy, completeness, diversity, balance, timeliness, and reproducibility.

