# Stage 40 — Run Summary Readability + CI Surface Parity

## Goal
Improve operator troubleshooting speed by producing a human-readable weekly run summary artifact and surfacing it directly in GitHub Actions job output.

## Changes shipped

1. Added markdown summary renderer:
   - `scripts/pipeline/run_summary_markdown.py`
   - Converts `artifacts/last_run.json` into `artifacts/last_run.md` with status, timings, missing artifacts, and failed-step details.

2. Wired markdown summary generation into weekly pipeline:
   - `scripts/pipeline/run_weekly.py`
   - After writing `artifacts/last_run.json`, pipeline now attempts to render `artifacts/last_run.md`.

3. Surfaced summary in CI job output:
   - `.github/workflows/weekly-editorial.yml`
   - Added `Publish run summary to Actions job output` step (`if: always()`) that writes `artifacts/last_run.md` to `$GITHUB_STEP_SUMMARY`.
   - Fallback to inline JSON when markdown artifact is absent.
   - Added markdown summary link in automated PR body quick links.

4. Updated runbook:
   - `docs/WEEKLY_PIPELINE.md`
   - Documented markdown summary artifact generation and Actions job summary behavior.

## Verification evidence

Local parity command:

```bash
python3 scripts/pipeline/run_summary_markdown.py --input artifacts/last_run.json --output artifacts/last_run.md
```

Expected result:
- `artifacts/last_run.md` is generated.
- File includes issue id, pipeline/artifact status, runtime telemetry, step-level timing lines, and missing-artifact/failed-step sections.

## Outcome
Weekly runs now emit both machine-readable and human-readable diagnostics, and CI exposes the readable summary directly in the workflow UI for faster triage without artifact download.
