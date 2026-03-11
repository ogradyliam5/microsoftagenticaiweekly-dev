---
id: playbook-agent-delivery-baseline
slug: agent-delivery-baseline
title: Agent Delivery Baseline
summary: A minimum operational baseline for shipping Microsoft-first agents with governance, observability, and controlled rollout.
status: published
updated_at: "2026-03-07T12:00:00Z"
checklist:
  - "Define release owner, incident owner, and rollback owner before first production deployment"
  - "Require canonical source links and confidence labels for every published issue item"
  - "Enforce pre-production validation gates for policy, permissions, and telemetry coverage"
  - "Gate promotion on evaluation and regression checks with explicit waiver logging"
  - "Document and test human escalation paths for tool failures and unsafe behavior"
anti_patterns:
  - "Publishing agent changes without clear runtime ownership"
  - "Relying on subjective readiness instead of measurable eval gates"
  - "Allowing one-off environment configuration with no reusable baseline"
  - "Treating observability as optional post-launch work"
metrics:
  - "Percent of releases passing mandatory eval gates"
  - "Mean time to rollback for failed or unsafe changes"
  - "Coverage of telemetry baseline across active agents"
  - "Incident rate per release ring"
---

# Agent Delivery Baseline

Use this playbook as the minimum operating standard for production agent delivery. It is designed for teams shipping weekly with approval-first governance.

## Release discipline

- Define release rings and promotion criteria in advance.
- Require evidence for waivers when a gate is bypassed.
- Tie publish approval to the same quality gates used for deployment approval.

## Governance discipline

- Keep policy controls versioned and environment-aware.
- Record tool-calling permissions and high-risk connector usage.
- Validate fallback behavior for critical agent actions.

## Operational discipline

- Publish escalation and rollback instructions in a single runbook.
- Track post-release incidents against release decisions.
- Update baselines when recurring failure modes are observed.
