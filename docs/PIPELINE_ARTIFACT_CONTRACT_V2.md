# Pipeline Artifact Contract v2

This file defines required artifact structures for the overhaul pipeline.

## 1) Editorial queue JSON
Path:
- `artifacts/editorial_queue-<issue_id>.json`

Required top-level fields:
- `contract_version` (must be `v2`)
- `issue_id`
- `generated_at`
- `window_start_utc`
- `window_end_utc`
- `items` (array)
- `excluded` (array)
- `mix_target`
- `mix_actual`
- `quality_summary`

Each `items[]` entry must include:
- `id`
- `title`
- `canonical_url`
- `publisher`
- `published_at_utc`
- `source_mix_bucket`
- `signal`
- `mini_abstract`
- `why_click`
- `confidence_label`
- `selection_reason`
- `score_total`
- `score_relevance`
- `score_quality`
- `score_freshness`
- `domain`

## 2) Curation manifest JSON
Path:
- `artifacts/curation_manifest-<issue_id>.json`

Required fields:
- `contract_version` (`v2`)
- `issue_id`
- `selected_item_ids`
- `excluded_items` with `reason_code`
- `reason_counts`
- `domain_diversity`
- `source_bucket_mix`
- `quality_gate_results`

Reason code examples:
- `duplicate`
- `low_relevance`
- `bland_summary`
- `domain_cap_exceeded`
- `missing_required_fields`
- `outside_collection_window`

## 3) Validation expectations
Validation must fail when:
- required fields are missing
- `contract_version != v2`
- banned filler patterns appear in `mini_abstract` or `why_click`
- composition constraints (8-10 target) are not met unless explicitly waived

## 4) Backward compatibility
`run_weekly.py` entrypoint remains compatible.

During migration, legacy outputs may coexist, but v2 artifacts are the contract for new implementation work.
