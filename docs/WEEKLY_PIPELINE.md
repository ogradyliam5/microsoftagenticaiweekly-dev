# Weekly Pipeline Runbook - v2 Target

This runbook defines the target weekly pipeline for the overhaul program.

Legacy scripts remain during migration, but new work should implement this contract.

## 1) Pipeline stages
1. `build_queue.py`
2. `validate_queue.py`
3. `generate_issue.py`
4. `render_issue_html.py` or Astro content writer
5. `run_report.py`
6. `source_candidate_audit.py`
7. `validate_issue_links.py`
8. `buttondown_draft.py` (draft only)
9. `run_weekly.py` orchestration + summary

## 2) Queue contract requirements (v2)
Each selected item must include:
- `signal`
- `mini_abstract`
- `why_click`
- `confidence_label`
- `selection_reason`
- provenance fields (canonical URL, publisher, publish date)
- quality score fields and diversity metadata

See [PIPELINE_ARTIFACT_CONTRACT_V2.md](PIPELINE_ARTIFACT_CONTRACT_V2.md).

## 3) Quality gates
Validation must fail on:
- missing title/canonical URL/published date
- duplicate canonical URLs in selected set
- banned filler patterns in mini-abstract or why-click fields
- evidence snippets over configured word limit
- source concentration above configured domain cap

## 4) Composition constraints
Default issue composition:
- 8-10 items
- Microsoft-first weighting
- adjacent ecosystem items only with direct implementation relevance
- balanced section distribution where feasible

## 5) Outputs per run
Required outputs:
- `artifacts/editorial_queue-<issue_id>.json`
- `artifacts/editorial_queue-<issue_id>.md`
- `artifacts/curation_manifest-<issue_id>.json`
- `posts/issue-<issue_id>.md` (or Astro content equivalent)
- `drafts/email-<issue_id>.md`
- `artifacts/run_report-<issue_id>.md`
- `artifacts/link_validation.json`
- `artifacts/link_validation.md`
- `artifacts/last_run.json`
- `artifacts/last_run.md`

Optional/non-blocking:
- source audit outputs

## 6) Approval gates (mandatory)
Human approval required before:
1. publishing website content
2. sending newsletter email
3. adding/removing tracked sources

## 7) Run commands
Local weekly run:
```bash
python3 scripts/pipeline/run_weekly.py
```

Targeted run:
```bash
python3 scripts/pipeline/run_weekly.py --issue-id 2026-10
```

Skip draft API call:
```bash
python3 scripts/pipeline/run_weekly.py --skip-buttondown
```

## 8) CI expectations
Weekly workflow must:
- run pipeline steps
- upload artifacts on success/failure
- validate summary contract
- run release audit checks
- open PR for review before publish/send

## 9) Migration note
Until Astro cutover is complete, maintain compatibility with existing entrypoints while producing v2-ready artifacts.
