# Source Candidate Audit Report

Generated: 2026-03-06T04:18:18Z

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
- Promotion opportunity top domains (5): medium.com, benediktbergmann.eu, benitezhere.blogspot.com, blog.allandecastro.com, d365goddess.com
  - Top-domain concentration: low (25.0% / 4 ids)
  - Top-domain candidate_reject share: 50.0% (2 ids)
    - candidate_add ids: itnext-medium, towards-data-science-llm
    - candidate_reject ids: medium-tag-microsoft365, medium-tag-powerplatform
  - Promotion top-domain detail (domain/count/ids):
    - medium.com: 4 (25.0%) reject_share=50.0% (itnext-medium, medium-tag-microsoft365, medium-tag-powerplatform, towards-data-science-llm)
    - benediktbergmann.eu: 1 (6.2%) reject_share=0.0% (benedikt-bergmann)
    - benitezhere.blogspot.com: 1 (6.2%) reject_share=0.0% (benitezhere)
    - blog.allandecastro.com: 1 (6.2%) reject_share=0.0% (allandecastro)
    - d365goddess.com: 1 (6.2%) reject_share=100.0% (d365goddess)
  - Promotion queue detail (rank/cohort/items):
    - #1: azure-sdk-blog (Azure SDK Blog) [candidate_add, items=25, domain=devblogs.microsoft.com, reason=machine_ingestable]
      - https://devblogs.microsoft.com/azure-sdk/feed/
    - #2: benitezhere (Benitez Here (Gonzalo Ruiz)) [candidate_add, items=25, domain=benitezhere.blogspot.com, reason=machine_ingestable]
      - https://benitezhere.blogspot.com/feeds/posts/default?alt=rss
    - #3: lowcodelewis (Low Code Lewis) [candidate_add, items=15, domain=lowcodelewis.com, reason=machine_ingestable]
      - https://lowcodelewis.com/feed/
    - #4: allandecastro (Allan De Castro) [candidate_add, items=10, domain=blog.allandecastro.com, reason=machine_ingestable]
      - https://www.blog.allandecastro.com/feed/
    - #5: benedikt-bergmann (Benedikt Bergmann) [candidate_add, items=10, domain=benediktbergmann.eu, reason=machine_ingestable]
      - https://benediktbergmann.eu/feed/
    - #6: itaintboring (It Ain't Boring (Alex Shlega)) [candidate_add, items=10, domain=itaintboring.com, reason=machine_ingestable]
      - https://www.itaintboring.com/feed/
    - #7: itnext-medium (ITNEXT on Medium) [candidate_add, items=10, domain=medium.com, reason=machine_ingestable]
      - https://medium.com/feed/itnext
    - #8: joegill (Joe Gill) [candidate_add, items=10, domain=joegill.com, reason=machine_ingestable]
      - https://joegill.com/feed/
    - #9: platformsofpower (Platforms of Power (Craig White)) [candidate_add, items=10, domain=platformsofpower.net, reason=machine_ingestable]
      - https://platformsofpower.net/feed/
    - #10: pwmather (Paul Mather) [candidate_add, items=10, domain=pwmather.wordpress.com, reason=machine_ingestable]
      - https://pwmather.wordpress.com/feed/
    - #11: towards-data-science-llm (Towards Data Science (LLM/agents scan)) [candidate_add, items=10, domain=medium.com, reason=machine_ingestable]
      - https://medium.com/feed/towards-data-science
    - #12: d365goddess (d365goddess) [candidate_reject, items=10, domain=d365goddess.com, reason=machine_ingestable]
      - https://d365goddess.com/feed/
    - #13: medium-tag-microsoft365 (medium-tag-microsoft365) [candidate_reject, items=10, domain=medium.com, reason=machine_ingestable]
      - https://medium.com/feed/tag/microsoft-365
    - #14: medium-tag-powerplatform (medium-tag-powerplatform) [candidate_reject, items=10, domain=medium.com, reason=machine_ingestable]
      - https://medium.com/feed/tag/power-platform
    - #15: mmsharepoint (mmsharepoint) [candidate_reject, items=10, domain=mmsharepoint.wordpress.com, reason=machine_ingestable]
      - https://mmsharepoint.wordpress.com/feed/
    - #16: powertricks (powertricks) [candidate_reject, items=10, domain=powertricks.io, reason=machine_ingestable]
      - https://powertricks.io/feed/
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

