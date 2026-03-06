# Stage 71 — Candidate Promotion Top-Domain Cohort Mix Parity

## Goal
Strengthen promotion-opportunity domain concentration triage with explicit cohort-mix metadata so reject-heavy concentration is visible without manual row inspection.

## Changes shipped
- Extended `scripts/pipeline/source_candidate_audit.py` summary output with:
  - `promotion_opportunity_top_domain_candidate_reject_id_count`
  - `promotion_opportunity_top_domain_candidate_reject_share_percent`
  - `promotion_opportunity_top_domain_candidate_reject_ids`
  - `promotion_opportunity_top_domain_candidate_add_ids`
- Enriched `promotion_opportunity_top_domains` rows with cohort-mix fields:
  - `candidate_add_ids`
  - `candidate_reject_ids`
  - `candidate_reject_share_percent`
- Updated markdown source-audit report to show top-domain reject share and explicit candidate-add/candidate-reject ID lists.
- Updated `docs/WEEKLY_PIPELINE.md` with the new top-domain cohort-mix parity fields.
- Regenerated source-audit artifacts:
  - `artifacts/source_candidate_audit.json`
  - `artifacts/source_candidate_audit.md`

## Verification
```bash
python3 scripts/pipeline/source_candidate_audit.py
```

Command completed successfully and rewrote source-audit artifacts with top-domain cohort-mix metadata.

## Dev preview parity
Stage changes governance pipeline script/docs and regenerated audit artifacts only; no homepage/template changes. Dev preview sync executed via `./scripts/sync-dev-site.sh` after commit.
