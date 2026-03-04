# Stage 48 — Run-History Index Parity

## Goal
Add canonical run-history index artifacts so operators can inspect retained run snapshots without manually listing `artifacts/run_history/`.

## Problem found
Run-history retention metadata existed in `artifacts/last_run.json`, but there was no standalone index artifact showing the retained snapshot set and paths in one place for CI/local troubleshooting.

## Changes shipped

1. `scripts/pipeline/run_weekly.py`
   - Added run-history index artifact generation on each successful summary write:
     - `artifacts/run_history/index.json`
     - `artifacts/run_history/index.md`
   - Extended `run_history` summary metadata with:
     - `index_json`
     - `index_markdown`
   - Added index artifacts to `output_artifacts` so existence checks are surfaced in `output_artifact_checks`.

2. `scripts/pipeline/run_summary_markdown.py`
   - Added run-history index paths to the markdown run summary section.

3. `scripts/pipeline/validate_last_run_summary.py`
   - Extended summary contract validation to require `run_history.index_json` and `run_history.index_markdown`.

4. `docs/WEEKLY_PIPELINE.md`
   - Updated run-summary metadata documentation to include run-history index paths.

## Verification

Local parity commands:

```bash
python3 scripts/pipeline/test_issue_id_guard.py
python3 scripts/pipeline/run_weekly.py --issue-id 2026-10 --skip-buttondown
python3 scripts/pipeline/validate_last_run_summary.py
```

Expected evidence:
- `artifacts/run_history/index.json` exists with retained snapshot entries.
- `artifacts/run_history/index.md` exists with human-readable retained snapshot listing.
- `artifacts/last_run.json` includes `run_history.index_json` and `run_history.index_markdown`.
- `artifacts/last_run.md` includes index paths in the run-history section.

## Outcome
Run-history retention is now paired with explicit index artifacts, giving deterministic local + CI visibility into exactly which run snapshots are retained.