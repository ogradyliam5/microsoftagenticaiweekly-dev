# Stage 16 — Pipeline Execution Modes (Backfill + Safe Local Run)

## Objective
Harden weekly execution flow so operators can:
1) regenerate a specific issue ID without date hacks, and
2) run locally without requiring Buttondown API access.

## Changes delivered
- `scripts/pipeline/run_weekly.py`
  - Added `--issue-id` override (e.g., `2026-10`) for deterministic reruns/backfills.
  - Added `--skip-buttondown` flag so content/site artifacts still generate when API auth is unavailable.
  - Added `buttondown` status to `artifacts/last_run.json` (`ok` / `skipped` / `failed_exit_<code>`).
- `docs/WEEKLY_PIPELINE.md`
  - Added documented examples for both new flags.

## Why this matters
- Removes friction for recovery/backfill work after pipeline changes.
- Keeps artifact generation unblocked in local/dev environments.
- Improves observability of whether Buttondown draft creation happened.

## Validation
- Ran: `python3 scripts/pipeline/run_weekly.py --issue-id 2026-10 --skip-buttondown`
- Confirmed artifact generation and updated `artifacts/last_run.json` with `buttondown: "skipped"`.
- Ran release audit script to verify site integrity checks still pass.
