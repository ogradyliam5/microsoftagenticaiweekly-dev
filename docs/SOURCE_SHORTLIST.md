# Source Governance (formerly Source Shortlist)

This document defines source governance rules. It is not a weekly snapshot log.

## Canonical source inventory
The canonical tracked source list is:
- `data/sources.json`

## Source inclusion standards
Include sources that are:
- reliable
- implementation-oriented
- consistently relevant to Microsoft agent delivery
- machine-ingestable where possible (RSS/Atom/API)

Exclude or down-rank sources that are:
- high-noise aggregators
- broad trend/news feeds without implementation detail
- inaccessible or unstable endpoints
- repetitive promotional channels

## Approval policy
Adding or removing tracked sources requires explicit Liam approval.

## Operational flow
1. Candidate discovery from audit artifacts.
2. Feed health check and relevance screening.
3. Approval decision.
4. Update `data/sources.json`.
5. Document rationale in PR notes.

## Required metadata per source
- `id`
- `name`
- `type`
- `url`
- `product_area`
- `trust`
- `priority`

## Audit references
Use pipeline artifacts for decisions:
- `artifacts/source_candidate_audit.json`
- `artifacts/source_candidate_audit.md`
