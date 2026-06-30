# Analyst Verification: <Feature>

> **Verdict:** DATA_PASS | DATA_FAIL
> **Spec:** docs/superpowers/specs/<feature>.md
> **Arch review:** docs/superpowers/reviews/arch-review-<feature>.md
> **Version:** <version from config if applicable>

## Independent Verification Method

- Command/script used: <how you ran it>
- Difference from Dev's path: <how your run differs>

## Phase ①: Reference Cases

| Case ID | Expected | Actual | Notes |
|---------|----------|--------|-------|
| case-1 | <value> | <value> | <match/mismatch> |
| case-2 | <value> | <value> | <match/mismatch> |

## Phase ②: Sample Set (e.g. 500 stocks)

- Hit rate: <value>
- False positive samples: <examples with dates/codes>
- Distribution notes: <anything unusual>

## Phase ③: Full Universe (if executed)

- Total samples: <N>
- Stability: <OK / issues>

## Conclusion & DATA BUG List (Dev)

- BUG-1: ts_code=xxx date=yyy expected=a actual=b — reproduction: `command`
- BUG-2: …

## Threshold/Semantics Suggestions (PO)

- <optional: recommendations for PO to consider>

## Handoff

- **Target:** <Developer (Dev) | Product Owner (PO)>
- **Address:** `docs/superpowers/reviews/<feature>-analyst-*.md` (this), `docs/superpowers/comms/<feature>.md`
- **Task:** <DATA_FAIL: fix bugs → Arch | DATA_PASS: product acceptance>
