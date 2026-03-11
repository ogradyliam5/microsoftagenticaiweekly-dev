# Design Directions - Overhaul Baseline

## Direction selected
Primary direction: `Premium Publication`.

This program intentionally moves away from dense dashboard styling and toward a reading-first editorial product.

## Design goals
- high readability at speed
- strong visual hierarchy
- low visual noise
- clear link intent
- consistent desktop/mobile behavior

## Core design principles
1. Typography leads the experience.
2. Information density is controlled by spacing, not heavy chrome.
3. Components are reusable and predictable.
4. Color supports hierarchy, not decoration.
5. Motion is subtle and purposeful.

## Token system requirements
Define explicit tokens for:
- color roles: background, surface, border, text, muted, accent, state
- typography: display, heading, body, meta, labels
- spacing scale
- radius and border
- focus and interaction states

## Component set required in v1
- global shell (header, footer, nav)
- hero block
- issue card
- signal card
- topic tile
- playbook card
- trust/provenance panel
- CTA modules (subscribe, archive, related links)

## Accessibility baseline
- WCAG-friendly contrast for text and controls
- visible focus states for keyboard users
- semantic headings and landmarks
- mobile readability first (small viewport before desktop expansion)

## Avoid
- dashboard-like clutter
- badge-heavy UIs with weak narrative flow
- oversized blocks of unbroken text
- decorative UI that does not improve comprehension

## Implementation note
The design system must be implemented as shared Astro components and tokens, not page-local ad hoc styles.
