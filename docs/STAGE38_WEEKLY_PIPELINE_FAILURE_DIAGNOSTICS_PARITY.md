# Stage 38 — Weekly Pipeline Failure Diagnostics Parity

## What changed
- Refactored `scripts/pipeline/run_weekly.py` to track core step execution state (`step_results`) and capture fail-fast diagnostics (`pipeline_status`, `failed_step`) in `artifacts/last_run.json`.
- Ensured summary writing still occurs when core pipeline commands fail so operators always get a machine-readable failure snapshot.
- Kept existing artifact integrity guardrails (`artifact_check`, `missing_artifacts`, `enforce_artifacts`) and made them coexist with pipeline-failure diagnostics.

## Verification
- `python3 scripts/pipeline/test_issue_id_guard.py`
- `python3 scripts/pipeline/run_weekly.py --issue-id 2026-10 --skip-buttondown --skip-source-audit`
- `python3 scripts/pipeline/run_weekly.py --issue-id 2026-54 --skip-buttondown --skip-source-audit` (expected guardrail failure)

## Notes
- Invalid `issue_id` input still exits before pipeline execution; this remains enforced by shared `issue_id_guard` logic.
- For runtime failures after validation, `artifacts/last_run.json` now includes step-level failure evidence for CI/local troubleshooting parity.
