# Stage 25 — Edition Data Consistency Pass

_Date: 2026-03-03 (UTC)_

## Scope executed

- Verified every edition card/link points to a valid issue page in `posts/`.
- Verified archive and RSS both cover all published issue pages with no missing/stale entries.
- Reconciled homepage date metadata with archive/RSS publication dates for:
  - `issue-2026-10`
  - `issue-2026-09`
- Regenerated missing legacy cover asset for the baseline sample issue:
  - `assets/covers/issue-000-cover.svg`

## Files changed

- `index.html`
- `assets/covers/issue-000-cover.svg`

## Verification output

```bash
python3 scripts/pipeline/release_audit.py --root .
# Audited HTML files: 16
# Published issues: 11
# Archive missing issues: none
# Feed missing issues: none
# Archive stale issues: none
# Feed stale issues: none
# Release audit OK

python3 - <<'PY'
# coverage + link + cover parity check
PY
# Issues: 11
# Archive missing: none
# Feed missing: none
# Index bad links: none
# Numeric issue covers missing: none
```

## Result

Stage 25 completed. Edition card metadata is now consistent across homepage/archive/feed coverage, and legacy issue cover parity has been restored for the sample baseline issue.
