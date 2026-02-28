# Source Shortlist (Daily Discovery Pass)

_Last updated: 2026-02-28 04:38 UTC_

Approval-first policy remains active: **no changes were made to `data/sources.json -> sources[]`**.
This pass only updates `candidates` with newly validated practitioner feeds.

## What changed this pass

### Added to `candidates.add` (new, validated)

1. **ReadyXRM (Nick Doelman)** — https://readyxrm.blog/feed/  
   - Why: High-signal practitioner coverage on Power Pages/Dataverse architecture and implementation.
   - Evidence:
     - https://readyxrm.blog/2026/02/26/the-end-of-power-pages-as-we-know-it/
     - https://readyxrm.blog/2026/02/18/power-pages-cache-conquered/

2. **Megan V. Walker** — https://meganvwalker.com/feed/  
   - Why: Frequent practical build posts (custom pages, connectors, business process flow implementation).
   - Evidence:
     - https://meganvwalker.com/show-loading-screen-in-your-custom-page/
     - https://meganvwalker.com/calculate-working-day-connector-in-power-automate/

3. **Nishant Rana** — https://nishantrana.me/feed/  
   - Why: Very high-cadence Dataverse/Dynamics troubleshooting with strong ALM/ops relevance.
   - Evidence:
     - https://nishantrana.me/2026/02/25/no-dependencies-shown-but-still-cant-delete-the-component-check-your-cloud-flows-dataverse-dynamics-365/
     - https://nishantrana.me/2026/02/24/solution-failed-to-import-missing-lookup-view-dependency-in-dataverse-dynamics-365/

4. **Elio Struyf** — https://www.eliostruyf.com/feed.xml  
   - Why: Individual M365 practitioner perspective; useful balance for M365 extensibility + AI engineering workflow content.
   - Evidence:
     - https://www.eliostruyf.com/killing-indie-development-with-ai/
     - https://www.eliostruyf.com/stop-typing-start-talking/

### Dedupe / hygiene

- Re-ran candidate dedupe by `id` and `url` in `candidates.add`.
- Retained existing pending candidates: `forwardforever`, `sharepains`, `michelcarlo`.

### Removed this pass

- **None.**

## Current recommendation for next approval gate

If approved, promote highest-priority practitioner candidates first in this order:
1) readyxrm
2) megan-v-walker
3) nishant-rana
4) forwardforever
5) sharepains
6) eliostruyf
7) michelcarlo

Rationale: maximizes practitioner signal, recency, and implementation depth across Copilot Studio/Dataverse/Power Platform while improving M365-extensibility coverage.
