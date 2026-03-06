# Stage 74 — Candidate-Reject Policy Block-Type Dominance Parity

## What changed
- Extended `scripts/pipeline/source_candidate_audit.py` summary output to add policy-block type percentage and dominance metadata for candidate-reject promotion opportunities:
  - `promotion_opportunity_candidate_reject_policy_blocked_percentages_by_type`
  - `promotion_opportunity_candidate_reject_policy_blocked_top_type`
  - `promotion_opportunity_candidate_reject_policy_blocked_top_type_share_percent`
  - `promotion_opportunity_candidate_reject_policy_blocked_top_type_ids`
- Added reusable helpers for deterministic percentage derivation and dominant block-type selection.
- Updated markdown audit rendering so policy-blocked breakdown lines include percentages and a one-line dominant policy block-type summary.
- Updated `docs/WEEKLY_PIPELINE.md` to document the new source-audit summary fields.

## Verification
- Regenerated source-candidate audit artifacts:

```bash
python3 scripts/pipeline/source_candidate_audit.py
```

- Confirmed new dominance/percentage fields in:
  - `artifacts/source_candidate_audit.json`
  - `artifacts/source_candidate_audit.md`

## Dev preview parity
Stage changes governance pipeline script/docs and regenerated audit artifacts only; no homepage/template changes. Dev preview sync executed via `./scripts/sync-dev-site.sh` after commit.
