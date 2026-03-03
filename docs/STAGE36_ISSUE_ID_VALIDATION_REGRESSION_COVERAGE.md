# Stage 36 — Issue-ID Validation Regression Coverage

## Objective
Lock in shared ISO week issue-id validation behavior with explicit regression checks, and enforce parity in CI before weekly pipeline argument construction.

## Changes shipped
- Added `scripts/pipeline/test_issue_id_guard.py`.
  - Covers format failures (`26-01`), week lower/upper bounds (`YYYY-00`, `YYYY-54`), and dynamic year-specific max-week checks.
  - Confirms validator accepts computed max week per year and rejects `max+1`.
- Updated `.github/workflows/weekly-editorial.yml`.
  - Added `Run issue-id validator regression checks` step.
  - Runs `python3 scripts/pipeline/test_issue_id_guard.py` before dispatch input argument build.
- Updated `docs/WEEKLY_PIPELINE.md`.
  - Documented CI guardrail execution and local parity command.

## Verification evidence
Local parity run:

```bash
python3 scripts/pipeline/test_issue_id_guard.py
# issue_id_guard regression tests: PASS
```

## Outcome
Issue-id validation behavior is now regression-checked in both local runs and scheduled/manual workflow execution paths, reducing the chance of silent parity drift.
