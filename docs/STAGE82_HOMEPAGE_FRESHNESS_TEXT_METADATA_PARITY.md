# Stage 82 — Homepage Freshness Text Metadata Parity

## Objective
Close remaining homepage drift risk where latest-edition links were correct but human-readable freshness text could silently fall behind RSS metadata.

## Changes shipped
- Extended `scripts/pipeline/release_audit.py` with RSS-first-item metadata checks:
  - Parse first feed item into `slug`, `week_label` (from title prefix), and full publication date.
  - Validate homepage hero freshness line (`Latest: ...`) includes expected week label + full date.
  - Validate latest-edition card metadata line includes expected week label + full date.
- Added explicit audit output fields for expected week/date metadata and freshness-line errors.
- Updated runbook in `docs/WEEKLY_PIPELINE.md` with freshness text parity behavior.

## Verification
```bash
python3 scripts/pipeline/release_audit.py --root .
```

Expected result:
- `Index latest-edition link errors: none`
- `Index latest-edition card errors: none`
- `Index freshness-line errors: none`
- `Release audit OK`

## Outcome
Homepage latest pathways now have both link-target parity and human-readable freshness-text parity against RSS first-item metadata, reducing stale-copy regressions before `develop -> main` promotion.
