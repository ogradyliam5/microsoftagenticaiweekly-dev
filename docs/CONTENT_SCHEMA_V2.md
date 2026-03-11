# Content Schema v2

This schema defines required frontmatter for Astro content collections.

## 1) Issue schema
Required fields:
- `id` (string, stable format `issue-...`; supports legacy numeric IDs and year-week IDs)
- `slug` (stable collection slug via filename or frontmatter override)
- `title` (string)
- `status` (`draft` | `scheduled` | `published` | `corrected`)
- `published_at` (ISO datetime)
- `updated_at` (ISO datetime)
- `summary` (string, <= 220 chars)
- `tags` (array of strings, 3-7 recommended)
- `confidence` (`low` | `medium` | `high`)
- `canonical_url` (absolute URL)
- `seo.meta_title` (string)
- `seo.meta_description` (string)

Recommended fields:
- `source_refs` (array of source IDs)
- `topics` (array of topic slugs)
- `playbooks` (array of playbook slugs)

## 2) Topic schema
Required fields:
- `id` (string)
- `slug` (stable collection slug via filename or frontmatter override)
- `title` (string)
- `summary` (string)
- `status` (`draft` | `published`)

Recommended fields:
- `related_topics` (array of slugs)
- `related_playbooks` (array of slugs)

## 3) Playbook schema
Required fields:
- `id` (string)
- `slug` (stable collection slug via filename or frontmatter override)
- `title` (string)
- `summary` (string)
- `status` (`draft` | `published`)
- `updated_at` (ISO datetime)

Recommended fields:
- `checklist` (array)
- `anti_patterns` (array)
- `metrics` (array)

## 4) Method/source policy schema
Required fields:
- `id` (string)
- `title` (string)
- `updated_at` (ISO datetime)
- `policy_version` (string)

## 5) Stability rules
- Slugs are stable after publish.
- Published issue IDs are immutable.
- Canonical URLs must not change without redirects.
- Note: `slug` is enforced by collection routing conventions, not by Zod schema fields.
