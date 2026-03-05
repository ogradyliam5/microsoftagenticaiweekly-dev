# Stage 67 — Candidate Promotion Queue Metadata Parity

## Goal
Expose richer, deterministic promotion-queue metadata so source approval triage can be done from one summary block without opening the full feed tables.

## Changes shipped
- Extended `scripts/pipeline/source_candidate_audit.py` summary output with:
  - `promotion_opportunity_rows` (ranked rows with `id`, `source_cohort`, `item_count`, `priority_rank`)
  - `promotion_opportunity_top_ids` (top 5 shortcut list)
  - `promotion_opportunity_cohort_percentages` (candidate-add vs candidate-reject split)
- Kept deterministic queue ordering parity (cohort priority -> item count desc -> id asc) and reused it for both ID list + ranked row metadata.
- Updated markdown report output (`artifacts/source_candidate_audit.md`) to surface:
  - cohort count + percentage breakdown
  - top-ID shortcut list
  - ranked queue detail lines (`#rank: id (cohort, items=N)`).
- Updated `docs/WEEKLY_PIPELINE.md` to document the new promotion queue metadata fields.
- Regenerated source-audit artifacts:
  - `artifacts/source_candidate_audit.json`
  - `artifacts/source_candidate_audit.md`

## Verification
```bash
python3 scripts/pipeline/source_candidate_audit.py
```

Command completed successfully and rewrote both source-audit artifacts with promotion queue metadata parity.

## Dev preview parity
Stage touches pipeline governance script/docs and regenerated artifacts only; no frontend template/layout changes. Dev preview sync executed via `./scripts/sync-dev-site.sh` after commit.
