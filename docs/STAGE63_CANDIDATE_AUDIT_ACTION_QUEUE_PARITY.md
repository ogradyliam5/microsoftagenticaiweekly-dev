# Stage 63 — Candidate Audit Action Queue Parity

## Objective
Make source governance triage directly actionable by emitting candidate/reject ID queues in both JSON and markdown artifacts.

## Changes shipped
- Updated `scripts/pipeline/source_candidate_audit.py`:
  - Added actionable summary arrays:
    - `candidate_add_promotion_candidate_ids`
    - `candidate_add_failed_ids`
    - `candidate_add_non_ingestable_ids`
    - `candidate_reject_revival_candidate_ids`
    - `candidate_reject_still_blocked_ids`
    - `candidate_reject_non_ingestable_ids`
  - Populated queues during candidate-add and candidate-reject audit traversal.
  - Extended markdown report with a new `Actionable triage queues` section for operator-fast review.
- Updated runbook documentation:
  - `docs/WEEKLY_PIPELINE.md`
- Regenerated source-audit artifacts:
  - `artifacts/source_candidate_audit.json`
  - `artifacts/source_candidate_audit.md`

## Verification
Local parity command:

```bash
python3 scripts/pipeline/source_candidate_audit.py
```

Observed evidence in `artifacts/source_candidate_audit.json` summary:
- `candidate_add_promotion_candidate_ids`: 11 IDs
- `candidate_add_failed_ids`: 4 IDs
- `candidate_reject_revival_candidate_ids`: 5 IDs
- `candidate_reject_still_blocked_ids`: 3 IDs

## Dev preview parity
Stage affects governance pipeline scripts/docs and regenerated artifacts only; no frontend template/layout changes. Dev preview sync executed via `./scripts/sync-dev-site.sh` after commit.
