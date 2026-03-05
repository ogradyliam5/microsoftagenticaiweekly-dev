# Source Candidate Audit Report

Generated: 2026-03-05T22:17:34Z

## Summary
- Candidate add feeds healthy: 11
- Candidate add feeds failing: 4
- Candidate add feeds non-ingestable: 0
  - due to no items: 0
  - due to unsupported root tag: 0
- Rejected feeds still blocked: 3
- Rejected feeds now healthy (review needed): 5
- Rejected feeds now machine-ingestable (promotion candidates): 5
- Rejected feeds now healthy but non-ingestable: 0

## Ingestability reason breakdown
- Candidate add dominant reason: machine_ingestable
- Candidate reject dominant reason: machine_ingestable
- Candidate add
  - machine_ingestable: 11 (73.3%)
  - no_items: 0 (0.0%)
  - unsupported_root_tag: 0 (0.0%)
  - fetch_failed: 4 (26.7%)
  - unknown: 0 (0.0%)
- Candidate reject
  - machine_ingestable: 5 (62.5%)
  - no_items: 0 (0.0%)
  - unsupported_root_tag: 0 (0.0%)
  - fetch_failed: 3 (37.5%)
  - unknown: 0 (0.0%)
- Candidate add minus reject percentage delta
  - machine_ingestable: +10.8 pp
  - no_items: +0.0 pp
  - unsupported_root_tag: +0.0 pp
  - fetch_failed: -10.8 pp
  - unknown: +0.0 pp

## Actionable triage queues
- Candidate add promotion-ready ids (11): allandecastro, azure-sdk-blog, benedikt-bergmann, benitezhere, itaintboring, itnext-medium, joegill, lowcodelewis, platformsofpower, pwmather, towards-data-science-llm
- Promotion opportunity queue ids (16): azure-sdk-blog, benitezhere, lowcodelewis, allandecastro, benedikt-bergmann, itaintboring, itnext-medium, joegill, platformsofpower, pwmather, towards-data-science-llm, d365goddess, medium-tag-microsoft365, medium-tag-powerplatform, mmsharepoint, powertricks
  - candidate_add: 11 (68.8%) | candidate_reject: 5 (31.2%)
- Promotion opportunity top ids (5): azure-sdk-blog, benitezhere, lowcodelewis, allandecastro, benedikt-bergmann
  - Promotion queue detail (rank/cohort/items):
    - #1: azure-sdk-blog (candidate_add, items=25)
    - #2: benitezhere (candidate_add, items=25)
    - #3: lowcodelewis (candidate_add, items=15)
    - #4: allandecastro (candidate_add, items=10)
    - #5: benedikt-bergmann (candidate_add, items=10)
    - #6: itaintboring (candidate_add, items=10)
    - #7: itnext-medium (candidate_add, items=10)
    - #8: joegill (candidate_add, items=10)
    - #9: platformsofpower (candidate_add, items=10)
    - #10: pwmather (candidate_add, items=10)
    - #11: towards-data-science-llm (candidate_add, items=10)
    - #12: d365goddess (candidate_reject, items=10)
    - #13: medium-tag-microsoft365 (candidate_reject, items=10)
    - #14: medium-tag-powerplatform (candidate_reject, items=10)
    - #15: mmsharepoint (candidate_reject, items=10)
    - #16: powertricks (candidate_reject, items=10)
- Candidate add failed ids (4): james-yao-medium, m365-platform-community, microsoft-ai-medium, nick-doelman-medium
- Candidate add non-ingestable ids (0): none
- Candidate add non-ingestable priority ids (0): none
  - machine_ingestable: none
  - no_items: none
  - unsupported_root_tag: none
  - fetch_failed: none
  - unknown: none
- Candidate reject revival-candidate ids (5): d365goddess, medium-tag-microsoft365, medium-tag-powerplatform, mmsharepoint, powertricks
- Candidate reject still-blocked ids (3): holgerimbery, the-custom-engine-github, tom-riha
- Candidate reject healthy-but-non-ingestable ids (0): none
- Candidate reject non-ingestable priority ids (0): none
  - machine_ingestable: none
  - no_items: none
  - unsupported_root_tag: none
  - fetch_failed: none
  - unknown: none

## Candidate Add Feed Checks
- `allandecastro` — OK — HTTP 200 — root: rss — items: 10 — ingestable — reason: machine_ingestable
- `benedikt-bergmann` — OK — HTTP 200 — root: rss — items: 10 — ingestable — reason: machine_ingestable
- `benitezhere` — OK — HTTP 200 — root: rss — items: 25 — ingestable — reason: machine_ingestable
- `itaintboring` — OK — HTTP 200 — root: rss — items: 10 — ingestable — reason: machine_ingestable
- `joegill` — OK — HTTP 200 — root: rss — items: 10 — ingestable — reason: machine_ingestable
- `lowcodelewis` — OK — HTTP 200 — root: rss — items: 15 — ingestable — reason: machine_ingestable
- `platformsofpower` — OK — HTTP 200 — root: rss — items: 10 — ingestable — reason: machine_ingestable
- `pwmather` — OK — HTTP 200 — root: rss — items: 10 — ingestable — reason: machine_ingestable
- `microsoft-ai-medium` — FAIL — HTTP 404 — root: n/a — items: 0 — non-ingestable — reason: fetch_failed
- `towards-data-science-llm` — OK — HTTP 200 — root: rss — items: 10 — ingestable — reason: machine_ingestable
- `itnext-medium` — OK — HTTP 200 — root: rss — items: 10 — ingestable — reason: machine_ingestable
- `nick-doelman-medium` — FAIL — HTTP 404 — root: n/a — items: 0 — non-ingestable — reason: fetch_failed
- `james-yao-medium` — FAIL — HTTP 404 — root: n/a — items: 0 — non-ingestable — reason: fetch_failed
- `azure-sdk-blog` — OK — HTTP 200 — root: rss — items: 25 — ingestable — reason: machine_ingestable
- `m365-platform-community` — FAIL — HTTP 404 — root: n/a — items: 0 — non-ingestable — reason: fetch_failed

## Rejected Feed Re-check
- `d365goddess` — NOW_OK — HTTP 200 — root: rss — items: 10 — ingestable — reason: machine_ingestable
- `holgerimbery` — STILL_BLOCKED — HTTP 404 — root: n/a — items: 0 — non-ingestable — reason: fetch_failed
- `medium-tag-microsoft365` — NOW_OK — HTTP 200 — root: rss — items: 10 — ingestable — reason: machine_ingestable
- `medium-tag-powerplatform` — NOW_OK — HTTP 200 — root: rss — items: 10 — ingestable — reason: machine_ingestable
- `mmsharepoint` — NOW_OK — HTTP 200 — root: rss — items: 10 — ingestable — reason: machine_ingestable
- `powertricks` — NOW_OK — HTTP 200 — root: rss — items: 10 — ingestable — reason: machine_ingestable
- `the-custom-engine-github` — STILL_BLOCKED — not well-formed (invalid token): line 21, column 75 — root: n/a — items: 0 — non-ingestable — reason: fetch_failed
- `tom-riha` — STILL_BLOCKED — HTTP 403 — root: n/a — items: 0 — non-ingestable — reason: fetch_failed

