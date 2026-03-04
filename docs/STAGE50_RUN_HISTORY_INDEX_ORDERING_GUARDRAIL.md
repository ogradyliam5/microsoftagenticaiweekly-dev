# Stage 50 — Run-History Index Ordering Guardrail

## Goal
Strengthen run-history index reliability by validating ordering and on-disk snapshot parity, not just count-level metadata.

## Problem found
Stage 49 validated index presence and count consistency, but did not enforce:
- deterministic descending chronology in `artifacts/run_history/index.json`,
- uniqueness of run stems,
- on-disk existence for each indexed snapshot path,
- explicit human-readable timestamp field per indexed run entry.

That left room for stale/reordered index entries to pass contract checks.

## Changes shipped

1. `scripts/pipeline/run_weekly.py`
   - Extended run-history index payload entries with `mtime_iso` for operator-readable snapshot chronology.
   - Extended `artifacts/run_history/index.md` snapshot bullets with `mtime` timestamp lines.

2. `scripts/pipeline/validate_last_run_summary.py`
   - Added strict run-history index entry validation for:
     - object shape per run entry,
     - unique non-empty `stem` values,
     - numeric `mtime` and non-empty `mtime_iso`,
     - descending `mtime` ordering,
     - existence of indexed JSON/markdown snapshot files on disk when paths are present.

3. `docs/WEEKLY_PIPELINE.md`
   - Updated CI guardrail note to include ordering + snapshot existence parity checks.

## Verification

Local parity command:

```bash
python3 scripts/pipeline/validate_last_run_summary.py
```

Expected evidence:
- Validator exits 0 for well-formed, descending, on-disk run-history index entries.
- Validator fails fast with explicit messages when index order, uniqueness, or snapshot parity drifts.

## Outcome
Run-history index validation now enforces chronological integrity and snapshot-path reality, reducing silent drift risk in CI/local release diagnostics.
