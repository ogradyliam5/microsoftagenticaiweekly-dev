# Stage 52 — Run-History Index Timestamp + Path Consistency Guardrail

## Goal
Harden `scripts/pipeline/validate_last_run_summary.py` so run-history index entries fail fast when timestamp or snapshot-path metadata drifts.

## Changes shipped

1. Added strict ISO-8601 UTC timestamp parsing helper (`_parse_utc_timestamp`) for summary/index validation.
2. Extended top-level summary validation to enforce:
   - `generated_at`, `run_started_at`, `run_finished_at` are valid UTC timestamps ending with `Z`
   - `run_finished_at >= run_started_at`
   - `generated_at >= run_started_at`
   - `run_duration_seconds` is numeric and non-negative
3. Extended run-history index validation to enforce:
   - `index.generated_at` is valid UTC timestamp
   - each `runs[].mtime_iso` is valid UTC timestamp and matches numeric `mtime` within 1 second
   - snapshot paths (JSON/markdown) use expected `artifacts/run_history/last_run-` prefix
   - when both JSON + markdown are present, their stems match each other and match `runs[].stem`

## Verification evidence

Local parity commands executed:

```bash
python3 scripts/pipeline/run_weekly.py --issue-id 2026-10 --skip-buttondown
python3 scripts/pipeline/validate_last_run_summary.py
```

Observed result:
- Weekly pipeline completed successfully with refreshed `artifacts/last_run.json` + run-history index artifacts.
- Summary contract validation passed with new timestamp/path guardrails enabled.

## Operator impact

- Any malformed/legacy timestamp drift in run summaries or run-history index now fails CI/local parity checks immediately.
- Any unexpected snapshot path prefix or mismatched stem pairing in run-history index entries now fails fast before promotion.
