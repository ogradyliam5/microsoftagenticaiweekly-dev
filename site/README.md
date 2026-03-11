# MAIW Astro Site

This directory contains the Astro site for Microsoft Agentic AI Weekly.

## Commands

From repository root:

```bash
npm run site:dev
npm run site:build
npm run site:preview
npm run site:check
```

From `site/` directly:

```bash
npm run dev
npm run build
npm run preview
npm run check
```

## Current scope

Implemented:
- Astro static site build and preview flow
- content collections for issues, topics, playbooks, and method
- shared design system components and layouts
- route set for home, latest, archive, topics, playbooks, method, sources, subscribe, corrections, and RSS

Behavior notes:
- Public routes prefer `published` collection entries.
- Draft entries remain in content for editorial work but are not surfaced unless no published entries exist.
- `npm run build` uses a wrapper that tolerates transient Windows `EBUSY` cleanup locks when output artifacts are present.
