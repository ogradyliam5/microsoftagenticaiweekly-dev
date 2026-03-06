# Stage 80 — Homepage Latest-Link Audit Parity

## What changed
- Extended `scripts/pipeline/release_audit.py` to validate homepage latest-edition link parity against RSS ordering.
- Added `latest_feed_issue_slug()` to read the first feed item as the canonical latest issue slug.
- Added `index_latest_links()` to inspect `index.html` anchors whose label includes `latest edition`.
- Added fail-fast release-audit errors when homepage latest-edition links are missing or point to a non-latest issue.
- Added release-audit output lines to show expected feed-latest slug and any homepage latest-link mismatches.

## Files changed
- `scripts/pipeline/release_audit.py`
- `docs/WEEKLY_PIPELINE.md`
- `docs/EXECUTION_QUEUE.md`
- `docs/STAGE80_HOMEPAGE_LATEST_LINK_AUDIT_PARITY.md`

## Verification
```bash
python3 scripts/pipeline/release_audit.py --root .
```

Observed:
- `Expected latest issue slug (feed first item): issue-2026-10`
- `Index latest-edition link errors: none`
- `Release audit OK`

## Dev preview parity
- Synced dev preview via `./scripts/sync-dev-site.sh` after commit/push.
