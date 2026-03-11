# Workstream Ownership Matrix

This file maps workstreams to non-conflicting file ownership.

## WS0 - Contracts
Owns:
- `docs/CONTENT_SCHEMA_V2.md`
- `docs/PIPELINE_ARTIFACT_CONTRACT_V2.md`
- `docs/DECISION_RECORDS.md`
- `docs/WORKSTREAM_OWNERSHIP.md`

## WS1 - Astro scaffold
Owns:
- `site/package.json`
- `site/astro.config.*`
- `site/tsconfig.json`
- `site/src/env.d.ts`
- `site/public/**`
- root `package.json` script delegation only

## WS2 - Design system
Owns:
- `site/src/styles/**`
- `site/src/layouts/**`
- `site/src/components/**`

## WS3 - Content collections and schema wiring
Owns:
- `site/src/content.config.*`
- `site/src/content/topics/**`
- `site/src/content/playbooks/**`
- `site/src/content/method/**`
- content-schema-related updates in `data/schemas/**`

## WS4 - Routes and RSS
Owns:
- `site/src/pages/**`

## WS5 - Pipeline v2
Owns:
- `scripts/pipeline/build_queue.py`
- `scripts/pipeline/validate_queue.py`
- `scripts/pipeline/generate_issue.py`
- `scripts/pipeline/render_issue_html.py`
- `scripts/pipeline/run_report.py`
- `scripts/pipeline/run_weekly.py`
- `scripts/pipeline/validate_last_run_summary.py`

## WS6 - Archive re-curation
Owns:
- `site/src/content/issues/**` (content files only)

## WS7 - Documentation rewrite
Owns:
- `docs/BRAND_BRIEF.md`
- `docs/DESIGN_DIRECTIONS.md`
- `docs/SITE_INFORMATION_ARCHITECTURE.md`
- `docs/PROJECT_PLAN.md`
- `docs/LAUNCH_CHECKLIST.md`
- `docs/WEEKLY_PIPELINE.md`
- `docs/OPERATING_HANDBOOK.md`
- `docs/DEPRECATED_DOCS.md`

## WS8 - Test and CI
Owns:
- `tests/**`
- `playwright.config.js`
- `.github/workflows/**`

## Coordination rules
- Each branch edits only owned paths.
- Cross-stream edits require integration PRs.
- Shared contracts must be updated before dependent implementation.
