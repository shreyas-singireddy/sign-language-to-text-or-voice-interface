# Gesture Dataset Health & Balance Report

This report audits coordinate record distribution, file sizes, and class balances within our gesture dataset archives.

## Dataset Volume
* **Total Samples**: 1080 sequences
* **Classes Audited**: 9

## Class Distribution Balance
| Gesture Label | Samples Count | Distribution % | Status |
|---|---|---|---|
| HELLO | 120 | 11.1% | [x] Healthy (Balanced) |
| THANKS | 120 | 11.1% | [x] Healthy (Balanced) |
| YES | 120 | 11.1% | [x] Healthy (Balanced) |
| NO | 120 | 11.1% | [x] Healthy (Balanced) |
| PLEASE | 120 | 11.1% | [x] Healthy (Balanced) |
| SORRY | 120 | 11.1% | [x] Healthy (Balanced) |
| HELP | 120 | 11.1% | [x] Healthy (Balanced) |
| GOOD MORNING | 120 | 11.1% | [x] Healthy (Balanced) |
| GOOD NIGHT | 120 | 11.1% | [x] Healthy (Balanced) |

## Integrity Audit Findings
* **Duplicate Samples**: 0 detected
* **Corrupt/Empty Samples**: 0 detected
* **Sequence Length Variance**: Healthy (standardized to 30 frames)
* **Status**: [x] Dataset is balanced, clean, and fully ready for model training.
