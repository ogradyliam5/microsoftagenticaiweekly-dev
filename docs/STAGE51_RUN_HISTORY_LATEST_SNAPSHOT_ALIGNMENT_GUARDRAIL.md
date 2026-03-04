# Stage 51 — Run-History Latest Snapshot Alignment Guardrail

## What changed

- Extended `scripts/pipeline/validate_last_run_summary.py` run-history index validation to enforce that the newest index entry (`runs[0]`) points to the same JSON + markdown snapshot paths recorded in:
  - `run_history.json`
  - `run_history.markdown`
- This adds explicit fail-fast detection for stale or drifted index pointers even when snapshot files still exist.
- Updated runbook wording in `docs/WEEKLY_PIPELINE.md` to include the new latest-entry alignment check in CI/local parity behavior.

## Why

Previous validation ensured index files existed, entries were sorted by mtime descending, and snapshots were present on disk. But it did not explicitly guarantee that the current run pointers (`run_history.*`) were represented as the newest retained run in the index. That gap could mask subtle pointer/index drift.

## Verification

Local parity command:

```bash
python3 scripts/pipeline/validate_last_run_summary.py
```

Expected result:

- Command exits `0` when run-history index latest entry and `run_history.*` pointers are aligned.
- Command exits non-zero with actionable error if index latest entry diverges from current run snapshot pointers.
