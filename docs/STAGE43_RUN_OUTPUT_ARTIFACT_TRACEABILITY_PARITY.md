# Stage 43 — Run Output Artifact Traceability Parity

## Goal
Make weekly run summaries easier to triage by recording named output artifact paths and presence status in both JSON and markdown summaries.

## Changes shipped

1. `scripts/pipeline/run_weekly.py`
   - Added `_build_output_artifacts(issue_id)` to define canonical named output paths.
   - Reused canonical output mapping when building required artifact checks.
   - Added `output_artifacts` and `output_artifact_checks` fields to `artifacts/last_run.json`.

2. `scripts/pipeline/run_summary_markdown.py`
   - Added `## Output artifacts` section that lists each named artifact with status (`present`/`missing`) and path.

3. `docs/WEEKLY_PIPELINE.md`
   - Documented `output_artifacts` and `output_artifact_checks` fields so local and CI operators have parity on what to inspect.

## Verification

Local parity command:

```bash
python3 scripts/pipeline/run_weekly.py --issue-id 2026-10 --skip-buttondown
```

Checks:

- `artifacts/last_run.json` includes:
  - `output_artifacts`
  - `output_artifact_checks`
- `artifacts/last_run.md` includes:
  - `## Output artifacts`
  - Per-artifact `present` / `missing` status lines.

## Outcome

Operators can now diagnose weekly output completeness from one summary artifact without manually cross-referencing file names, improving CI/local troubleshooting speed.
