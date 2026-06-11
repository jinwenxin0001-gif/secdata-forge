# Drift Report

- Overall status: **update_required**
- Features checked: **9**

## Numeric Drift

| Feature | PSI | KS | Severity |
| --- | ---: | ---: | --- |
| src_port | 0.1561 | 0.1667 | medium |
| dst_port | 0.7619 | 0.1333 | high |
| duration | 3.7949 | 0.4 | high |
| src_bytes | 1.803 | 0.4667 | high |
| dst_bytes | 0.0835 | 0.1333 | low |
| packets | 3.4169 | 0.3667 | high |

## Categorical Drift

| Feature | JS Divergence | Severity |
| --- | ---: | --- |
| protocol | 0.0018 | low |
| label | 0.0707 | medium |
| attack_type | 0.038 | low |
