# Stage 62 — Candidate Audit Dominant-Reason Delta Signal

## Objective
Improve source-triage readability by surfacing the dominant ingestability reason per cohort and the percentage-point delta between candidate-add vs candidate-reject reason distributions.

## Changes shipped
- Updated `scripts/pipeline/source_candidate_audit.py`:
  - Added dominant reason helper (`_top_reason`) and summary fields:
    - `summary.candidate_add_top_ingestability_reason`
    - `summary.candidate_reject_top_ingestability_reason`
  - Added percentage-point delta helper (`_reason_percentage_delta`) and summary field:
    - `summary.candidate_add_vs_reject_reason_percentage_delta`
  - Extended markdown audit rendering to show:
    - dominant reason for each cohort
    - reason percentage deltas (`candidate add - candidate reject`) in `pp` format.
- Regenerated source-audit artifacts:
  - `artifacts/source_candidate_audit.json`
  - `artifacts/source_candidate_audit.md`
- Updated runbook documentation:
  - `docs/WEEKLY_PIPELINE.md`

## Verification
Local parity command:

```bash
python3 scripts/pipeline/source_candidate_audit.py
```

Observed evidence in `artifacts/source_candidate_audit.json`:
- `candidate_add_top_ingestability_reason = machine_ingestable`
- `candidate_reject_top_ingestability_reason = machine_ingestable`
- `candidate_add_vs_reject_reason_percentage_delta.machine_ingestable = +10.8`
- `candidate_add_vs_reject_reason_percentage_delta.fetch_failed = -10.8`

## Outcome
Approval triage now gets instant directional context (dominant reason + cohort deltas) without manual comparison across multiple summary maps.
