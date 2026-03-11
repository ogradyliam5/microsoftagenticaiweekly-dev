# MAIW Complete Overhaul - Multi-Agent Execution Plan

## 1) Goal and locked decisions
- Keep name: `Microsoft Agentic AI Weekly`.
- Rebuild as a premium, readable intelligence product.
- Migrate from ad-hoc static HTML to Astro SSG.
- Keep approval-first publish/send workflow.
- Weekly format: curated briefing, default 8-10 items.
- Voice: neutral but sharp, no persona-based prescriptive language.
- Summary format: mini-abstract optimized for "should I click?" decisions.
- Coverage: Microsoft-first + adjacent items with direct implementation relevance.
- Scope includes Topics + Playbooks in v1.

## 2) Parallel workstreams (non-conflicting file ownership)

## WS0 - Contracts and integration guardrails (single owner)
**Purpose:** lock shared interfaces before parallel implementation.

**Owns files/paths**
- `docs/CONTENT_SCHEMA_V2.md` (new)
- `docs/PIPELINE_ARTIFACT_CONTRACT_V2.md` (new)
- `docs/DECISION_RECORDS.md` (new)
- `docs/WORKSTREAM_OWNERSHIP.md` (new)

**Outputs**
- Final issue frontmatter contract.
- Final topic/playbook schema contract.
- Final queue artifact `v2` contract (`mini_abstract`, `why_click`, `confidence_label`, `selection_reason`, quality/diversity metadata).
- Freeze list for file ownership.

**Dependencies:** none  
**Blocks:** WS2, WS3, WS4, WS5, WS6

---

## WS1 - Astro platform scaffold
**Purpose:** stand up Astro project and build pipeline without touching editorial logic.

**Owns files/paths**
- `site/**` project scaffolding only:
  - `site/package.json`
  - `site/astro.config.*`
  - `site/tsconfig.json`
  - `site/src/env.d.ts`
  - `site/public/**` (static assets bootstrap)
- root scripts updates needed to run site build:
  - `package.json` (root script delegation only)

**Outputs**
- Working Astro app skeleton.
- Build and local preview commands.
- Base deployment-ready structure.

**Dependencies:** none  
**Blocks:** WS2, WS3, WS4, WS8

---

## WS2 - Design system and shared UI components
**Purpose:** implement publication-first visual system and reusable primitives.

**Owns files/paths**
- `site/src/styles/**`
- `site/src/layouts/**`
- `site/src/components/**`

**Outputs**
- Design tokens (type/color/spacing/radius/border/state).
- Shared components:
  - hero
  - issue cards
  - signal cards
  - topic tiles
  - playbook cards
  - trust/provenance panels
  - CTA modules
- Responsive + a11y baseline in shared UI.

**Dependencies:** WS0 contracts, WS1 scaffold  
**Blocks:** WS4 pages, WS8 UI tests

---

## WS3 - Content collections and schema enforcement
**Purpose:** define and enforce Astro content model for issues/topics/playbooks/method.

**Owns files/paths**
- `site/src/content.config.*`
- `site/src/content/issues/**` (structure/templates only in this stream)
- `site/src/content/topics/**` (initial seed structure)
- `site/src/content/playbooks/**` (initial seed structure)
- `site/src/content/method/**`
- `data/schemas/**` updates related to content schema

**Outputs**
- Strict frontmatter schema validation.
- Slug stability rules for topic/playbook routes.
- Initial seed content templates for each collection.

**Dependencies:** WS0 contracts, WS1 scaffold  
**Blocks:** WS4 pages, WS6 archive re-curation, WS8 content validation tests

---

## WS4 - Astro routes, navigation, and RSS
**Purpose:** implement the new page model using WS2 components + WS3 collections.

**Owns files/paths**
- `site/src/pages/index.*`
- `site/src/pages/archive.*`
- `site/src/pages/about.*`
- `site/src/pages/subscribe.*`
- `site/src/pages/corrections.*`
- `site/src/pages/topics/**`
- `site/src/pages/playbooks/**`
- `site/src/pages/posts/**`
- `site/src/pages/feed.xml.*` (or Astro RSS endpoint)
- `site/src/pages/sources.*` / method pages

**Outputs**
- Full route set:
  - Home
  - Latest Issue
  - Archive
  - Topics hub/detail
  - Playbooks hub/detail
  - About/Method
  - Subscribe
  - Corrections
  - RSS
- Consistent global nav/footer and internal linking.

**Dependencies:** WS2, WS3  
**Blocks:** WS8 e2e coverage, final cutover

---

## WS5 - Pipeline v2 (automation + quality gates)
**Purpose:** upgrade weekly pipeline to produce high-quality structured summaries and enforce anti-slop gates.

**Owns files/paths**
- `scripts/pipeline/build_queue.py`
- `scripts/pipeline/validate_queue.py`
- `scripts/pipeline/generate_issue.py`
- `scripts/pipeline/render_issue_html.py` (or replacement that outputs Astro-ready content)
- `scripts/pipeline/run_report.py`
- `scripts/pipeline/run_weekly.py`
- `scripts/pipeline/validate_last_run_summary.py`
- `artifacts/*` contract shape docs/examples

**Outputs**
- Queue contract `v2` with required fields.
- Quality gates:
  - duplication
  - blandness/boilerplate rejection
  - source concentration caps
  - weak relevance filtering
- Composition constraints (8-10 target, Microsoft+adjacent balance).
- Curation manifest artifact with inclusion/exclusion reason codes.
- Backward-compatible `run_weekly.py` entrypoint.

**Dependencies:** WS0 contracts  
**Blocks:** WS6 automated re-curation support, WS8 pipeline tests

---

## WS6 - Full archive re-curation (parallelized substreams)
**Purpose:** re-curate all historical issues to new editorial standard.

**Owns files/paths**
- `site/src/content/issues/**` content files only

**Substreams (no overlap)**
- WS6A: earliest third of issues
- WS6B: middle third of issues
- WS6C: newest third of issues

**Outputs**
- Every issue rewritten to canonical story unit:
  - Signal
  - Mini-abstract
  - Why click
  - Source confidence
- Normalized metadata, tags, confidence, canonical URLs.
- Link-health verified for all issue sources.

**Dependencies:** WS3 schema, WS5 tooling/helpers  
**Blocks:** WS8 content QA, launch sign-off

---

## WS7 - Docs and operating model rewrite
**Purpose:** replace fragmented documentation with aligned operating handbook.

**Owns files/paths**
- `docs/BRAND_BRIEF.md`
- `docs/DESIGN_DIRECTIONS.md`
- `docs/SITE_INFORMATION_ARCHITECTURE.md`
- `docs/PROJECT_PLAN.md`
- `docs/LAUNCH_CHECKLIST.md`
- `docs/WEEKLY_PIPELINE.md`
- `docs/OPERATING_HANDBOOK.md` (new)
- decommission list in `docs/DEPRECATED_DOCS.md` (new)

**Outputs**
- Unified narrative across brand, design, IA, pipeline, and launch governance.
- Explicit approval-first policy in user-facing and operator docs.
- Weekly QA checklist and release checklist.

**Dependencies:** WS0 contracts (for accuracy)  
**Blocks:** final documentation sign-off

---

## WS8 - Test + CI hardening
**Purpose:** add regression safety for new platform and pipeline.

**Owns files/paths**
- `tests/**`
- `playwright.config.js`
- `.github/workflows/**`
- site/pipeline test fixtures as needed

**Outputs**
- Unit tests:
  - scoring
  - dedupe
  - diversity limits
  - summary quality lint rules
- Snapshot tests for rendered issues and metadata validity.
- E2E tests:
  - nav integrity
  - theme behavior
  - subscribe path
  - archive/topic/playbook routes
- Accessibility checks in CI (contrast, heading order, keyboard navigation, link semantics).
- Release audit checks for latest issue parity across home/archive/RSS.

**Dependencies:** WS4, WS5, WS6  
**Blocks:** launch readiness

## 3) Dependency graph and execution order
1. Start immediately in parallel: WS0, WS1.
2. Once WS0 + WS1 are merged: WS2, WS3, WS5, WS7 can run in parallel.
3. Once WS2 + WS3 are merged: WS4 starts.
4. Once WS3 (+ optionally WS5 helpers) are merged: WS6A/B/C run in parallel.
5. Once WS4 + WS5 + WS6 are merged: WS8 finalizes test/CI and release guardrails.
6. Final integration + cutover (single integrator) after WS8 passes.

## 4) Merge protocol to avoid agent conflicts
- One workstream per branch: `ws0-contracts`, `ws1-astro-scaffold`, etc.
- Each workstream may only edit owned paths.
- Cross-stream changes require an integration PR, never direct edits in another stream branch.
- Shared contracts in WS0 are read-only after freeze unless integration lead approves revision.
- Rebase daily against `integration/main-overhaul` branch.
- Require passing stream-specific checks before merge.

## 5) Done criteria (program level)
- Astro site fully replaces legacy static pages with all required routes.
- Queue artifact contract published as `v2` and enforced in validators.
- All historical issues re-curated to new standard.
- Unified docs set complete; contradictory legacy docs deprecated.
- CI passes all unit/snapshot/e2e/accessibility/release-audit checks.
- Approval-first publish/send policy visible in product and operations docs.
