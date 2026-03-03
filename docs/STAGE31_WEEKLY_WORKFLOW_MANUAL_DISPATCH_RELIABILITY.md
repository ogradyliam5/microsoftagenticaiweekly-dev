# Stage 31 — Weekly Workflow Manual-Dispatch Reliability

## Objective
Ensure manual workflow runs are reliable by bypassing the Monday 08:00 Europe/London schedule gate when the workflow is triggered via `workflow_dispatch`.

## Changes made
1. Updated `.github/workflows/weekly-editorial.yml` gate step:
   - `workflow_dispatch` now sets `run_pipeline=true` immediately.
   - Scheduled runs still require Monday 08:00 Europe/London.
   - Skip message clarified for scheduled non-window executions.
2. Updated `docs/WEEKLY_PIPELINE.md` GitHub Actions section:
   - Added explicit note that manual dispatch bypasses time gate.

## Why this matters
Previously, manual dispatches outside Monday 08:00 London time were gated out, making on-demand recovery/backfill runs unreliable. This fix keeps scheduled behavior strict while restoring deterministic operator-triggered runs.

## Local parity check
```bash
sed -n '1,120p' .github/workflows/weekly-editorial.yml
```

## Outcome
Stage 31 complete: manual workflow dispatch is now reliable without weakening scheduled-run guardrails.
