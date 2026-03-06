# Stage 73 — Candidate-Reject Policy-Blocked Promotion Signal Parity

## What changed
- Extended `scripts/pipeline/source_candidate_audit.py` to carry policy metadata for promotion-opportunity rows sourced from `candidates.reject`:
  - `policy_reject_reason`
  - `policy_block_type` (normalized buckets: `publication_noise`, `topic_noise`, `community_forum`, `stale_or_low_signal`, `manual_review_hold`, `other_policy`)
- Added summary-level policy-blocked queue metrics for candidate-reject promotions:
  - `promotion_opportunity_candidate_reject_policy_blocked_ids`
  - `promotion_opportunity_candidate_reject_policy_blocked_count`
  - `promotion_opportunity_candidate_reject_policy_blocked_share_percent`
  - `promotion_opportunity_candidate_reject_policy_blocked_ids_by_type`
  - `promotion_opportunity_candidate_reject_policy_blocked_counts_by_type`
- Added top-domain policy-risk visibility fields:
  - `promotion_opportunity_top_domain_policy_blocked_ids`
  - `promotion_opportunity_top_domain_policy_blocked_count`
  - `promotion_opportunity_top_domain_policy_blocked_share_percent`
- Updated markdown audit rendering to show:
  - candidate-reject policy-blocked queue summary,
  - policy-blocked type breakdown,
  - top-domain policy-blocked share,
  - per-row policy metadata in promotion queue detail.
- Updated `docs/WEEKLY_PIPELINE.md` with the new policy-blocked promotion signal fields.

## Verification
- Regenerated source-candidate audit artifacts:

```bash
python3 scripts/pipeline/source_candidate_audit.py
```

- Confirmed new policy metadata and summary fields in:
  - `artifacts/source_candidate_audit.json`
  - `artifacts/source_candidate_audit.md`

## Dev preview parity
Stage changes governance pipeline script/docs and regenerated audit artifacts only; no homepage/template changes. Dev preview sync executed via `./scripts/sync-dev-site.sh` after commit.
