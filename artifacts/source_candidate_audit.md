# Source Candidate Audit Report

Generated: 2026-03-05T11:33:50Z

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

