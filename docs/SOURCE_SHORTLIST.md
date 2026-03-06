# Source Shortlist (Stage 1 Stabilization)

_Last updated: 2026-03-06 06:30 UTC_

No core `sources[]` promotions in this run (approval-first policy preserved). This pass focused on individual-practitioner discovery quality: two new practitioner candidates added; four broad/non-individual candidate feeds removed from intake.

## Promoted to core sources (approved set)

- `futurework-blog` — Future Work (Vesa Nopanen)
- `reshmee-auckloo` — Reshmee Auckloo
- `baeke` — Geert Baeke
- `rob-quickenden` — Rob Quickenden
- `karlex` — Karl-Johan Spiik (Karlex)
- Prior approved practitioner additions retained in core:
  - `forwardforever`
  - `megan-v-walker`
  - `nishant-rana`
  - `readyxrm`
  - `eliostruyf`
  - `sharepains`
  - `michelcarlo`

## Discovery candidates pending approval

### New in this run

- `journeyofthegeek` — Journey Of The Geek (Eric Woodruff) (`https://journeyofthegeek.com/feed/`)
  - Why: independent architect perspective with recent Azure AI Foundry + Defender for AI deep-dives and strong governance/operations relevance.
- `nikki-chapple` — Nikki Chapple (`https://nikkichapple.com/feed/`)
  - Why: active individual-practitioner M365 source with Copilot readiness/compliance and tenant ops coverage useful for weekly governance filtering.

### Existing candidates retained

- `allandecastro` — Allan De Castro (`https://www.blog.allandecastro.com/feed/`)
- `benedikt-bergmann` — Benedikt Bergmann (`https://benediktbergmann.eu/feed/`)
- `benitezhere` — Benitez Here (Gonzalo Ruiz) (`https://benitezhere.blogspot.com/feeds/posts/default?alt=rss`)
- `itaintboring` — It Ain't Boring (Alex Shlega) (`https://www.itaintboring.com/feed/`)
- `joegill` — Joe Gill (`https://joegill.com/feed/`)
- `lowcodelewis` — Low Code Lewis (`https://lowcodelewis.com/feed/`)
- `nick-doelman-medium` — Nick Doelman (Medium author feed) (`https://medium.com/feed/@readyxrm`)
- `james-yao-medium` — James Yao (Medium author feed) (`https://medium.com/feed/@james.yao`)
- `platformsofpower` — Platforms of Power (Craig White) (`https://platformsofpower.net/feed/`)
- `pwmather` — Paul Mather (`https://pwmather.wordpress.com/feed/`)

## Removed from candidate intake (this run)

- `microsoft-ai-medium`
  - Rationale: official publication duplicates existing Microsoft official coverage and is not individual-practitioner-led.
- `towards-data-science-llm`
  - Rationale: high-volume publication feed with weak individual-practitioner signal and high topical noise.
- `itnext-medium`
  - Rationale: publication feed (not individual) with broad topic drift and low Microsoft-specific precision.
- `m365-platform-community`
  - Rationale: forum board feed is discussion-heavy and not a practitioner blog source.

## Rejected / excluded (keep out of automated ingestion)

- `d365goddess` — feed reachable; still excluded pending manual quality/topicality review
- `holgerimbery` — 404 feed endpoint
- `medium-tag-microsoft365` — high-noise tag aggregator
- `medium-tag-powerplatform` — high-noise tag aggregator
- `mmsharepoint` — stale cadence for current weekly format
- `powertricks` — endpoint healthy; excluded pending manual quality/topicality review
- `the-custom-engine-github` — non-blog/non-feed manual-watch item
- `tom-riha` — 403 feed endpoint (blocked to automated retrieval)

## Validation notes

- Dedupe check completed against existing `sources[]` ids + URLs before updating candidates.
- No core `sources[]` changes made (approval-first policy preserved).
- New additions validated as reachable RSS feeds and screened for agentic-AI-weekly fit (Copilot/Foundry/governance-ops weighting).
- Candidate pruning favored individual practitioner signal over publication/forum-scale noise.
