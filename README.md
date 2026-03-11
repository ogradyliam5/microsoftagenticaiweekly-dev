# Microsoft Agentic AI Weekly

Engineering and editorial source for `Microsoft Agentic AI Weekly`, a practitioner-focused newsletter covering the Microsoft agentic AI ecosystem.

## Intent
`Microsoft Agentic AI Weekly` exists to help builders quickly understand what changed, what matters, and what is actionable each week across agentic AI tools, platforms, and practices.

The project is designed to:
- Cut through hype with source-grounded, verifiable reporting
- Translate weekly updates into practical implications for teams shipping real systems
- Maintain a repeatable editorial and publishing workflow with audit visibility

Primary audience:
- Engineers and architects building agentic AI systems
- Technical leads evaluating tooling, patterns, and platform direction
- Practitioners who need concise weekly signal, not noisy trend summaries

## What this repo contains
- Astro static site architecture in [`site/`](site/)
- Pipeline v2 for weekly curation and quality-gated mini-abstract summaries
- Historical archive content and publication assets
- Multi-agent runbooks and operational documentation

## Quick start
From the repository root:

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start local preview:
   ```bash
   npm run site:dev
   ```
3. Open `http://localhost:4321`

For a production-style local preview:

```bash
npm run site:build
npm run site:preview
```

## GitHub Pages deployment
- The site deploys automatically from GitHub Actions on every push to `main`.
- Manual deploys are available via the `deploy-pages` workflow (`workflow_dispatch`).
- Ensure repository settings use Pages source: `GitHub Actions`.

## Script reference

| Command | Purpose |
| --- | --- |
| `npm run site:dev` | Start Astro dev server from repo root |
| `npm run site:build` | Build the Astro site |
| `npm run site:preview` | Preview the built Astro site locally |
| `npm run site:check` | Run Astro checks |
| `npm run build:css` | Build root Tailwind CSS assets |
| `npm run build` | Alias for `build:css` |
| `npm run test:e2e` | Run Playwright end-to-end tests |

## Repository map

| Path | Purpose |
| --- | --- |
| [`site/`](site/) | Astro app, routes, components, and content collections |
| [`posts/`](posts/) | Issue content and newsletter source material |
| [`docs/`](docs/) | Operating handbook, pipeline docs, launch/runbook docs |
| [`scripts/`](scripts/) | Automation scripts (pipeline, Buttondown, sync helpers) |
| [`artifacts/`](artifacts/) | Generated outputs and audit artifacts |
| [`drafts/`](drafts/) | Working drafts for issues and email content |
| [`assets/`](assets/) | Shared static assets and styles |
| [`tests/`](tests/) | Playwright test suite |

## Start here
- [plan.md](plan.md)
- [AGENT.md](AGENT.md)
- [docs/OPERATING_HANDBOOK.md](docs/OPERATING_HANDBOOK.md)
- [docs/WEEKLY_PIPELINE.md](docs/WEEKLY_PIPELINE.md)

## Core principles
- Approval-first publish and send
- Source-grounded editorial quality
- Clear, concise, non-hype writing
- Repeatable weekly operations with visible audit artifacts

## Legacy compatibility
Legacy root `.html` routes (for example `index.html`, `archive.html`, `about.html`) are maintained as redirect shims to canonical Astro routes to prevent drift during transition.
