# Stage 10 — Interesting-Only Source Ranking

Date: 2026-03-02

## Scope delivered

Implemented ranking changes to prioritize high-signal practitioner content (updates, guides, how-tos, demos, build reports) and down-rank generic marketing/noise.

## Changes made

- Updated `scripts/pipeline/build_queue.py`:
  - Added `classify_content_type(title)` classifier.
  - Added explicit `CONTENT_TYPE_WEIGHTS` map.
  - Folded content-type weighting into `quality_score(...)`.
  - Rebalanced total scoring formula to `freshness*0.50 + quality*0.50`.
  - Added queue item fields:
    - `content_type`
    - `score_content_type`
  - Expanded `scoring_notes` with explicit content-type explanation.
  - Updated Markdown queue report top-candidate section to show content type + weight.

- Regenerated queue artifacts for current issue:
  - `artifacts/editorial_queue-2026-09.json`
  - `artifacts/editorial_queue-2026-09.md`

## Validation

```bash
python3 scripts/pipeline/build_queue.py --issue-id 2026-09
python3 scripts/pipeline/validate_queue.py --issue-id 2026-09
```

Result: `Validation OK: 24 items`

## Outcome

Queue ranking now explicitly reflects content intent, with practical implementation content elevated and lower-signal marketing/news recaps reduced in priority.
