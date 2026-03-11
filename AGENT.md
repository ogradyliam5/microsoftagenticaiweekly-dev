# MAIW Agent Brief (Canonical)

This file is the canonical operating brief for any agent working in this repository.

## Mission
Build and operate `Microsoft Agentic AI Weekly` as a premium, readable, high-trust briefing product.

## Program status
The project is in a full overhaul program:
- Static HTML site -> Astro SSG
- Legacy queue contract -> queue contract v2
- Legacy issue style -> curated mini-abstract style
- Fragmented docs -> unified operating handbook

Use [plan.md](plan.md) as the execution backbone.

## Locked decisions (do not re-open without explicit approval)
- Keep publication name: `Microsoft Agentic AI Weekly`
- Weekly issue target: 8-10 items
- Voice: neutral but sharp
- No persona-based instructions (no "if you are X, do Y")
- Coverage: Microsoft-first plus adjacent items with direct implementation relevance
- Topics + Playbooks are in v1 scope
- Approval-first is mandatory for publish/send/source-list changes

## Non-negotiables
1. No autonomous publish.
2. No autonomous email send.
3. No tracked-source add/remove without Liam approval.
4. No invented facts, dates, claims, or quotes.
5. Every published item must have provenance (canonical URL, publisher, date, confidence label).

## Canonical docs (read in this order)
1. [plan.md](plan.md)
2. [docs/OPERATING_HANDBOOK.md](docs/OPERATING_HANDBOOK.md)
3. [docs/DECISION_RECORDS.md](docs/DECISION_RECORDS.md)
4. [docs/CONTENT_SCHEMA_V2.md](docs/CONTENT_SCHEMA_V2.md)
5. [docs/PIPELINE_ARTIFACT_CONTRACT_V2.md](docs/PIPELINE_ARTIFACT_CONTRACT_V2.md)
6. [docs/WORKSTREAM_OWNERSHIP.md](docs/WORKSTREAM_OWNERSHIP.md)

## Required output model
Every issue item must map to this canonical story unit:
- `Signal`
- `Mini-abstract`
- `Why click`
- `Source confidence`

## Anti-slop quality bar
Reject or rewrite copy that contains generic filler, repetitive templates, or unsupported claims.

Banned patterns include:
- "It still adds practical context"
- "Use it to ... before broad rollout" without source-grounded specifics
- duplicated sentence structures across multiple items

## Working rules for multi-agent execution
- Respect file ownership defined in [docs/WORKSTREAM_OWNERSHIP.md](docs/WORKSTREAM_OWNERSHIP.md).
- Do not edit files owned by another active workstream.
- Integration changes happen in integration PRs only.
- Update contracts before implementation if interface changes are required.

## Delivery definition of done
- Astro site fully replaces legacy static pages.
- Pipeline emits v2 queue artifacts and curation manifest.
- Full archive is re-curated to new editorial standard.
- CI validates routing, accessibility, metadata, and release parity.
- Approval-first policy is visible in product and operations docs.
