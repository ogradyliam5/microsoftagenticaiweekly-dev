# Site Information Architecture (Redesign)

## 1) Purpose and Positioning

This redesign shifts the site from a Power Platform-adjacent newsletter to a **broader Microsoft Agentic AI intelligence hub** for builders, architects, and technical leaders.

### Positioning statement

> Microsoft Agentic AI Weekly helps teams design, ship, and operate production-grade AI agents across the Microsoft ecosystem — including Azure AI, Copilot stack, Microsoft 365 extensibility, data/security/governance layers, and community-built tooling.

### Audience segments

- **Hands-on builders**: engineers creating agents, tools, prompts, orchestration, and observability.
- **Platform owners**: architects and leads responsible for standards, security, cost, and lifecycle.
- **Decision makers**: product/IT leaders deciding where to invest and what to standardize.

### Content pillars (beyond Power Platform)

1. Agent engineering patterns (architecture, orchestration, memory, tools, evals)
2. Azure AI + model/platform capability changes
3. Copilot ecosystem (M365, Copilot Studio, extensibility)
4. Data, security, governance, and compliance for agent workloads
5. DevEx and operations (MCP, telemetry, CI/CD, testing, incident handling)
6. Community/open ecosystem signals (independent blogs, OSS, field lessons)

---

## 2) Proposed Page Model

## Core pages

- **Home (`/`)**
  - Mission, latest issue, key categories, quick trust signals, subscribe CTA.
- **Issue Detail (`/posts/issue-###.html`)**
  - Full weekly issue with sectioned brief, commentary, and action items.
- **Archive (`/archive.html`)**
  - Chronological issue index with filters (topic, maturity, audience).
- **Topics Hub (`/topics.html`)** *(new)*
  - Landing page for thematic navigation and editorial taxonomy.
- **Topic Detail (`/topics/{slug}.html`)** *(new, generated static pages)*
  - Curated list of issue excerpts/articles under a specific topic.
- **Playbooks (`/playbooks.html`)** *(new)*
  - Evergreen practical guidance (e.g., governance checklist, rollout blueprint, telemetry starter).
- **Sources & Method (`/sources.html`)**
  - Sourcing policy, evidence standards, weighting model, submission path.
- **Corrections (`/corrections.html`)**
  - Transparent correction log with timestamps and issue references.
- **About (`/about.html`)**
  - Editorial charter, target audience, bias/independence notes, contact.
- **Subscribe (`/subscribe.html`)** *(new; can redirect to Buttondown/form if preferred)*
  - Dedicated conversion page with value proposition and expectations.

## Utility/SEO pages

- **Search (`/search.html`)** *(optional phase 2)*
- **Tag index (`/tags.html`)** *(optional phase 2)*
- **RSS (`/feed.xml`)**
- **Robots / sitemap (`/robots.txt`, `/sitemap.xml`)**

---

## 3) Navigation Model

## Primary navigation

- Home
- Latest Issue
- Archive
- Topics
- Playbooks
- Sources
- About
- Subscribe (button-style CTA)

## Secondary navigation patterns

- **Within issue pages**:
  - Jump links: Summary, Signals, Deep Dives, Build Next, Tooling, Governance, Watchlist, References.
- **Topic breadcrumbs**:
  - Home → Topics → Topic Name → Item/Issue.
- **Cross-linking blocks**:
  - “Related topics” and “Related playbooks” on issue entries.

## Footer navigation

- Corrections
- Editorial policy
- Submission/contact
- RSS
- Privacy/terms (when added)

---

## 4) Page Content Blocks (Reusable Components)

## Global blocks

- **Hero block**: positioning + primary CTA + social proof snippet.
- **Trust bar**: source mix %, last updated, correction policy link.
- **Newsletter CTA block**: compact inline signup/subscribe.

## Home blocks

1. **Hero + current thesis**
2. **Latest issue card**
3. **This week’s top 3 signals**
4. **Topic tiles** (architecture, ops, security, ecosystem, etc.)
5. **Playbooks highlight**
6. **Editorial method snapshot** (independent-first policy)
7. **Subscribe CTA + archive link**

## Issue detail blocks

1. **Issue header** (number, date, reading time, audience tags)
2. **Executive summary** (3-5 bullets)
3. **Signal cards** (what changed / why it matters / who should care)
4. **Deep dive sections**
5. **Build-next checklist** (immediate practical actions)
6. **Risks & caveats**
7. **Referenced sources list**
8. **Related issue/topic links**
9. **Subscribe + feedback CTA**

## Topic page blocks

- Topic summary and scope
- Canonical “start here” entries
- Recent updates
- Related playbook links

## Playbook blocks

- Context/problem
- Recommended pattern
- Anti-patterns
- Implementation checklist
- Operational metrics
- Review cadence

---

## 5) Metadata Schema (Content + SEO + Editorial)

Use front matter (or equivalent JSON data) per issue/article:

```yaml
id: "issue-012"
title: "Agent Operations Maturity: From Demo to Durable"
slug: "agent-operations-maturity-demo-to-durable"
type: "issue" # issue | playbook | topic-note
status: "published" # draft | scheduled | published | corrected
published_at: "2026-03-05T09:00:00Z"
updated_at: "2026-03-05T11:20:00Z"
issue_number: 12
summary: "Weekly high-signal brief on agent operations, governance, and tooling."
reading_time_minutes: 9
audience:
  - builders
  - architects
  - leaders
categories:
  - agent-engineering
  - operations
  - governance
tags:
  - mcp
  - telemetry
  - copilot-studio
  - azure-ai
products_mentioned:
  - azure-ai-foundry
  - copilot-studio
  - microsoft-365-copilot
stage:
  - build
  - operate
confidence: "medium" # low | medium | high
editorial_weight:
  independent_pct: 65
  official_pct: 35
cta_primary: "subscribe"
cta_secondary: "read-related-playbook"
canonical_url: "https://microsoftagenticaiweekly.com/posts/issue-012.html"
seo:
  meta_title: "Microsoft Agentic AI Weekly #012 — Agent Operations Maturity"
  meta_description: "What changed in Microsoft Agentic AI this week and what builders should do next."
  og_image: "/assets/og/issue-012.png"
  noindex: false
```

### Source-level metadata (per cited link)

```yaml
source_id: "src-2026-03-05-07"
url: "https://example.com/post"
source_type: "independent" # independent | official | vendor | community
publisher: "Example Blog"
author: "Jane Doe"
published_at: "2026-03-03"
claim_type: "announcement" # benchmark | opinion | tutorial | release-note | incident
verification_status: "reviewed" # pending | reviewed | disputed
relevance_score: 4 # 1-5
```

---

## 6) Taxonomy (Topics + Tags)

## Recommended top-level topics

- Agent Architecture
- Tooling & MCP
- Data & Retrieval
- Security & Governance
- Evaluation & Observability
- Copilot Ecosystem
- Azure AI Platform
- Enterprise Rollout & ALM
- Community Signals

## Tag rules

- Use specific product/tech tags (e.g., `azure-ai-foundry`, `copilot-studio`, `mcp`, `rag`).
- Avoid broad duplicates (`ai`, `microsoft`) unless required for legacy compatibility.
- 3-7 tags per issue for consistency.

---

## 7) URL and Naming Conventions

- Keep issue URLs stable: `/posts/issue-###.html`
- Topic URLs: `/topics/{kebab-case}.html`
- Playbook URLs: `/playbooks/{kebab-case}.html`
- File slugs should be lowercase kebab-case.
- Do not change published issue URLs after indexing; use canonical and redirects if needed.

---

## 8) Acceptance Criteria (Redesign Definition of Done)

## IA and navigation

- [ ] Primary nav includes Home, Latest Issue, Archive, Topics, Playbooks, Sources, About, Subscribe.
- [ ] Users can reach any published issue within 2 clicks from Home.
- [ ] Topic structure exists with at least 6 seeded topics.

## Positioning and messaging

- [ ] Homepage copy explicitly states scope beyond Power Platform.
- [ ] At least 4 content pillars are visible on Home or Topics.
- [ ] About page reflects editorial charter for full Microsoft agent ecosystem coverage.

## Content model and metadata

- [ ] All new issues use standardized front matter schema.
- [ ] Source entries include `source_type` and `verification_status`.
- [ ] Feed and social metadata use issue-level canonical and OG data.

## Quality and governance

- [ ] Corrections page links from footer and issue pages.
- [ ] Sources page documents independent-vs-official weighting policy.
- [ ] Minimum one “Build next” action is present per major section in issue pages.

## Technical/SEO baseline

- [ ] Sitemap includes Home, Archive, Topics, Playbooks, latest 20 issues.
- [ ] Each indexable page has unique title + meta description.
- [ ] Internal links validated (no broken nav links).

---

## 9) Suggested Rollout (Phased)

1. **Phase 1 (IA foundation)**: nav update, Topics hub, metadata schema adoption.
2. **Phase 2 (depth)**: topic pages + seeded playbooks + richer issue templates.
3. **Phase 3 (optimization)**: search/tag index, conversion tuning, structured data enrichment.

This sequence limits redesign risk while immediately signaling the broader Microsoft Agentic AI positioning.
