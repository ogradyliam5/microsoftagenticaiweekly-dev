# Stage 39 — Weekly Pipeline Runtime Telemetry Parity

## What changed
- Extended `scripts/pipeline/run_weekly.py` run summary output to include run-level timestamps and duration:
  - `run_started_at`
  - `run_finished_at`
  - `run_duration_seconds`
- Added per-step runtime telemetry (`started_at`, `finished_at`, `duration_seconds`) to all recorded steps in `step_results`.
- Preserved existing failure diagnostics and artifact integrity guardrails so timing evidence coexists with fail-fast and troubleshooting metadata.
- Updated `docs/WEEKLY_PIPELINE.md` to document runtime telemetry fields and operator expectations.

## Verification
- `python3 scripts/pipeline/test_issue_id_guard.py`
- `python3 scripts/pipeline/run_weekly.py --issue-id 2026-10 --skip-buttondown --skip-source-audit`

## Notes
- Runtime telemetry is written to `artifacts/last_run.json` for both local and CI parity.
- Existing `generated_at` remains present for backward compatibility with prior consumers.
