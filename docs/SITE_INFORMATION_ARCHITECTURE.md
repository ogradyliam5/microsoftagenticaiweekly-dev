# Site Information Architecture - v1 Overhaul

## 1) Product model
The site is a weekly publication with two supporting knowledge surfaces:
- `Topics` for navigable thematic grouping
- `Playbooks` for evergreen practical guidance

## 2) Route model (Astro target)
Core routes:
- `/` Home
- `/posts/[slug]` Issue detail pages
- `/archive` Issue archive
- `/topics` Topics hub
- `/topics/[slug]` Topic detail pages
- `/playbooks` Playbooks hub
- `/playbooks/[slug]` Playbook detail pages
- `/about` Method and editorial charter
- `/sources` Source policy and governance
- `/corrections` Correction policy and changelog
- `/subscribe` Subscribe page
- `/feed.xml` RSS feed

## 3) Navigation model
Primary nav:
- Home
- Latest Issue
- Archive
- Topics
- Playbooks
- Sources
- About
- Subscribe

Footer nav:
- Corrections
- Editorial policy
- RSS

## 4) Issue page structure
1. Issue header (title, week label, publication date)
2. Executive summary (short)
3. Signal list (canonical story units)
4. Related topics/playbooks
5. Source index
6. Corrections/report link

## 5) Content taxonomy
Top-level topics (seed set):
- Agent Architecture
- Tooling and MCP
- Data and Retrieval
- Security and Governance
- Evaluation and Observability
- Copilot Ecosystem
- Azure AI Platform
- Enterprise Rollout and ALM

Tag rules:
- 3-7 tags per issue
- specific technology tags over broad terms
- stable slugs for topics/playbooks

## 6) IA acceptance criteria
- Any issue reachable in <=2 clicks from Home.
- Latest issue is obvious from Home and nav.
- Topics and Playbooks are first-class surfaces.
- All public pages have unique title/description metadata.
