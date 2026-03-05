# Stage 61 — Candidate Audit Reason-Percentage Parity

## Objective
Add cohort-level ingestability reason percentages for candidate-add and candidate-reject feeds so source triage can quickly see weighting (not just raw counts).

## Changes shipped
- Updated `scripts/pipeline/source_candidate_audit.py`:
  - Added `_reason_percentages(...)` helper that computes rounded cohort percentages per ingestability reason.
  - Added summary maps:
    - `summary.candidate_add_reason_percentages`
    - `summary.candidate_reject_reason_percentages`
  - Updated markdown audit rendering so reason breakdown lines include `count (percent%)`.
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

Observed summary evidence in `artifacts/source_candidate_audit.json`:
- `candidate_add_reason_percentages.machine_ingestable = 73.3`
- `candidate_add_reason_percentages.fetch_failed = 26.7`
- `candidate_reject_reason_percentages.machine_ingestable = 62.5`
- `candidate_reject_reason_percentages.fetch_failed = 37.5`

## Outcome
Candidate source triage now has both absolute reason counts and normalized percentages, making approval/rejection prioritization faster without changing approval-first governance policy.
