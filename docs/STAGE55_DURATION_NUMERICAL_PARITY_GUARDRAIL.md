# Stage 55 — Duration Numerical Parity Guardrail

## Goal
Harden `artifacts/last_run.json` contract validation so runtime duration fields cannot drift away from their timestamp bounds without failing CI/local parity checks.

## Changes shipped

1. Extended `scripts/pipeline/validate_last_run_summary.py` with a shared tolerance constant:
   - `DURATION_TOLERANCE_SECONDS = 5.0`

2. Added run-level duration parity validation:
   - `run_duration_seconds` must be within 5 seconds of `run_finished_at - run_started_at`.

3. Added step-level duration parity validation:
   - For non-failed steps, `duration_seconds` must be within 5 seconds of `finished_at - started_at`.
   - For failed steps that include both `started_at` and numeric `duration_seconds`, enforce the same parity check.
   - Preserve existing support for failed steps where `started_at` and/or `duration_seconds` are null.

## Verification

Local parity command:

```bash
python3 scripts/pipeline/validate_last_run_summary.py
```

Result on current artifact:
- Passes successfully with the new duration parity guardrails enabled.

## Outcome
Malformed or stale duration telemetry now fails fast in both local and CI validation flows, reducing silent drift between timestamps and numeric runtime fields.
