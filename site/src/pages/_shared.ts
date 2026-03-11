import type { CollectionEntry } from "astro:content";

export const SITE_TITLE = "Microsoft Agentic AI Weekly";
export const SITE_DESCRIPTION =
  "Microsoft-first weekly intelligence briefing on agentic AI implementation signals.";

export const NAV_LINKS = [
  { href: "/", label: "Home" },
  { href: "/latest", label: "Latest" },
  { href: "/archive", label: "Archive" },
  { href: "/topics", label: "Topics" },
  { href: "/playbooks", label: "Playbooks" },
  { href: "/about", label: "Method" },
  { href: "/subscribe", label: "Subscribe" },
  { href: "/corrections", label: "Corrections" },
  { href: "/sources", label: "Sources" },
];

export function dateLabel(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleDateString("en-GB", {
    year: "numeric",
    month: "short",
    day: "2-digit",
    timeZone: "UTC",
  });
}

export function sortIssuesDesc(entries: CollectionEntry<"issues">[]) {
  return [...entries].sort((left, right) => {
    return (
      new Date(right.data.published_at).getTime() -
      new Date(left.data.published_at).getTime()
    );
  });
}

export function preferPublishedIssues(entries: CollectionEntry<"issues">[]) {
  const published = entries.filter((entry) => entry.data.status === "published");
  return published.length ? published : entries;
}

export function preferPublishedTopics(entries: CollectionEntry<"topics">[]) {
  const published = entries.filter((entry) => entry.data.status === "published");
  return published.length ? published : entries;
}

export function preferPublishedPlaybooks(entries: CollectionEntry<"playbooks">[]) {
  const published = entries.filter((entry) => entry.data.status === "published");
  return published.length ? published : entries;
}

export function issuePath(issue: CollectionEntry<"issues">): string {
  return `/posts/${issue.slug}`;
}

export function topicPath(topic: CollectionEntry<"topics">): string {
  return `/topics/${topic.slug}`;
}

export function playbookPath(playbook: CollectionEntry<"playbooks">): string {
  return `/playbooks/${playbook.slug}`;
}

export function normalizeStatus(status: string): string {
  return status.replaceAll("-", " ");
}

export function isNavActive(activePath: string, href: string): boolean {
  if (!activePath) {
    return false;
  }
  if (href === "/") {
    return activePath === "/";
  }
  return activePath === href || activePath.startsWith(`${href}/`);
}
