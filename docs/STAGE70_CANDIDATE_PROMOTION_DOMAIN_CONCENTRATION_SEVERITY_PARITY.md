# Stage 70 — Candidate Promotion Domain Concentration Severity Parity

## Goal
Strengthen promotion-opportunity domain signals with explicit concentration percentages and a severity label so source-approval triage can detect diversity risk immediately.

## Changes shipped
- Extended `scripts/pipeline/source_candidate_audit.py` summary output with:
  - `promotion_opportunity_domain_percentages`
  - `promotion_opportunity_top_domain_share_percent`
  - `promotion_opportunity_top_domain_id_count`
  - `promotion_opportunity_domain_concentration_level` (`none`/`low`/`medium`/`high`)
- Enriched `promotion_opportunity_top_domains` rows with `percent` metadata.
- Updated markdown source-audit report to show top-domain percentage detail and concentration severity line.
- Updated `docs/WEEKLY_PIPELINE.md` with the new concentration-parity fields.
- Regenerated source-audit artifacts:
  - `artifacts/source_candidate_audit.json`
  - `artifacts/source_candidate_audit.md`

## Verification
```bash
python3 scripts/pipeline/source_candidate_audit.py
```

Command completed successfully and rewrote source-audit artifacts with percentage + concentration severity metadata.

## Dev preview parity
Stage changes governance pipeline script/docs and regenerated audit artifacts only; no homepage/template changes. Dev preview sync executed via `./scripts/sync-dev-site.sh` after commit.
