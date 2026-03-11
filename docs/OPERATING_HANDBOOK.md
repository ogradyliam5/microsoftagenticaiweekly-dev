# Operating Handbook - Overhaul Program

## 1) Why this exists
This handbook is the operational source of truth for the MAIW overhaul.

Use this with:
- [plan.md](../plan.md)
- [WORKSTREAM_OWNERSHIP.md](WORKSTREAM_OWNERSHIP.md)
- [CONTENT_SCHEMA_V2.md](CONTENT_SCHEMA_V2.md)
- [PIPELINE_ARTIFACT_CONTRACT_V2.md](PIPELINE_ARTIFACT_CONTRACT_V2.md)

## 2) Operating model
Weekly cycle:
1. Collect candidate signals.
2. Build + validate queue.
3. Generate issue and email drafts.
4. Review queue and drafts.
5. Approve publish/send decisions.
6. Publish site and send email only after explicit approval.

## 3) Editorial standard
Each signal must include:
- Signal
- Mini-abstract
- Why click
- Source confidence

Quality rules:
- concise language
- no repeated boilerplate
- source-grounded claims only
- clear provenance

## 4) Technical target state
- Astro SSG for all site surfaces.
- Structured content collections for issues, topics, playbooks, and method pages.
- Pipeline v2 queue contract with curation manifest.
- CI checks for routing, metadata, quality gates, and release parity.

## 5) Governance controls
Mandatory approvals:
- site publish
- newsletter send
- tracked-source changes

Required evidence per run:
- queue artifacts
- run report
- run summary
- draft content outputs

## 6) Multi-agent coordination
- Respect workstream ownership boundaries.
- Use integration PRs for cross-stream changes.
- Freeze shared contracts early to avoid merge churn.

## 7) Definition of ready for launch
- Full archive re-curated.
- All required routes and docs in place.
- Pipeline v2 contract active.
- CI and release audits green.
- Approval-first policy visible and enforceable.
