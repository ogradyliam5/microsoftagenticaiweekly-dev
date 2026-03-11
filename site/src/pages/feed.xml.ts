import type { APIRoute } from "astro";
import { getCollection } from "astro:content";
import { preferPublishedIssues, sortIssuesDesc } from "./_shared";

function xmlEscape(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

export const GET: APIRoute = async ({ site }) => {
  const allIssues = sortIssuesDesc(await getCollection("issues"));
  const fallback = preferPublishedIssues(allIssues);
  const base = site?.toString().replace(/\/$/, "") ?? "https://microsoftagenticaiweekly.com";

  const items = fallback
    .slice(0, 50)
    .map((issue) => {
      const issueUrl = `${base}/posts/${issue.slug}`;
      const pubDate = new Date(issue.data.published_at).toUTCString();
      return [
        "<item>",
        `<title>${xmlEscape(issue.data.title)}</title>`,
        `<link>${xmlEscape(issueUrl)}</link>`,
        `<guid>${xmlEscape(issueUrl)}</guid>`,
        `<pubDate>${xmlEscape(pubDate)}</pubDate>`,
        `<description>${xmlEscape(issue.data.summary)}</description>`,
        "</item>",
      ].join("");
    })
    .join("");

  const body = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    "<rss version=\"2.0\">",
    "<channel>",
    "<title>Microsoft Agentic AI Weekly</title>",
    `<link>${xmlEscape(`${base}/`)}</link>`,
    "<description>Microsoft-first weekly intelligence briefing for agentic AI implementation teams.</description>",
    "<language>en-gb</language>",
    items,
    "</channel>",
    "</rss>",
  ].join("");

  return new Response(body, {
    headers: {
      "Content-Type": "application/rss+xml; charset=utf-8",
    },
  });
};
