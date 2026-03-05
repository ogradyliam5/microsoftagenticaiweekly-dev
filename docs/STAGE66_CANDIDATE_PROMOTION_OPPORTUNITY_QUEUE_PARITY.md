# Stage 66 — Candidate Promotion Opportunity Queue Parity

## Goal
Add a deterministic single queue for promotion-ready feeds so approval triage can start from one ordered list instead of manually merging candidate-add and candidate-reject outputs.

## Changes shipped
- Extended `scripts/pipeline/source_candidate_audit.py` summary output with:
  - `promotion_opportunity_ids`
  - `promotion_opportunity_breakdown` (`candidate_add`, `candidate_reject`)
- Added deterministic promotion queue ordering:
  1. cohort priority (`candidate_add` before `candidate_reject`)
  2. feed item count (descending)
  3. id (ascending, deterministic tie-break)
- Updated source-audit markdown output with the promotion-opportunity queue and cohort breakdown line.
- Updated `docs/WEEKLY_PIPELINE.md` to document the new promotion queue metadata.
- Regenerated source audit artifacts:
  - `artifacts/source_candidate_audit.json`
  - `artifacts/source_candidate_audit.md`

## Verification
```bash
python3 scripts/pipeline/source_candidate_audit.py
```

Command completed successfully and rewrote both source-audit artifacts with promotion-opportunity queue metadata.

## Dev preview parity
Stage touches governance pipeline script/docs and regenerated artifacts only; no frontend template/layout changes. Dev preview sync executed via `./scripts/sync-dev-site.sh` after commit.
