import { defineCollection, z } from 'astro:content';

// Slug stability rules:
// - Slugs are stable after publish for topics and playbooks
// - Published issue IDs are immutable
// - Canonical URLs must not change without redirects

// Issue schema
const issueSchema = z.object({
  id: z.string().regex(/^issue-[a-z0-9-]+$/),
  title: z.string(),
  status: z.enum(['draft', 'scheduled', 'published', 'corrected']),
  published_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  summary: z.string().max(220),
  tags: z.array(z.string()).min(3).max(7),
  confidence: z.enum(['low', 'medium', 'high']),
  canonical_url: z.string().url(),
  seo: z.object({
    meta_title: z.string(),
    meta_description: z.string(),
  }),
  source_refs: z.array(z.string()).optional(),
  topics: z.array(z.string()).optional(),
  playbooks: z.array(z.string()).optional(),
}).strict();

// Topic schema
const topicSchema = z.object({
  id: z.string().regex(/^topic-[a-z0-9-]+$/),
  title: z.string(),
  summary: z.string(),
  status: z.enum(['draft', 'published']),
  related_topics: z.array(z.string()).optional(),
  related_playbooks: z.array(z.string()).optional(),
}).strict();

// Playbook schema
const playbookSchema = z.object({
  id: z.string().regex(/^playbook-[a-z0-9-]+$/),
  title: z.string(),
  summary: z.string(),
  status: z.enum(['draft', 'published']),
  updated_at: z.string().datetime(),
  checklist: z.array(z.string()).optional(),
  anti_patterns: z.array(z.string()).optional(),
  metrics: z.array(z.string()).optional(),
}).strict();

// Method/source policy schema
const methodSchema = z.object({
  id: z.string().regex(/^method-[a-z0-9-]+$/),
  title: z.string(),
  updated_at: z.string().datetime(),
  policy_version: z.string(),
}).strict();

export const collections = {
  issues: defineCollection({
    type: 'content',
    schema: issueSchema,
  }),
  topics: defineCollection({
    type: 'content',
    schema: topicSchema,
  }),
  playbooks: defineCollection({
    type: 'content',
    schema: playbookSchema,
  }),
  method: defineCollection({
    type: 'content',
    schema: methodSchema,
  }),
};
