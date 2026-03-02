#!/usr/bin/env python3
import argparse
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]


def speaker(item):
    if "Official" in item.get("tags", []):
        return "Microsoft"
    return item.get("publisher") or "Community"


def concise_summary(item):
    title = (item.get("title") or "").strip()
    custom = (item.get("why_it_matters") or "").strip()
    title_l = title.lower()

    rules = [
        (["copilot studio", "mcp"], "Concrete Copilot Studio build pattern teams can reuse quickly."),
        (["dataverse", "search"], "Improves retrieval quality for Dataverse-grounded copilots."),
        (["roadmap", "spfx"], "Signals near-term platform changes likely to impact planning and maintenance."),
        (["rbac", "authentication"], "Practical security testing approach for auth and role boundaries."),
    ]
    for keys, text in rules:
        if all(k in title_l for k in keys):
            return text

    if custom and "potentially relevant update" not in custom.lower():
        return custom
    return f"{title} — useful if this is in your active delivery scope."


def card(item):
    title = html.escape(item.get("title", "Untitled"))
    by = html.escape(speaker(item))
    summary = html.escape(concise_summary(item))
    url = html.escape(item.get("canonical_url", item.get("url", "#")))
    return f'<article class="signal-card"><h3>{title}</h3><p><strong>{by}:</strong> {summary}</p><p class="small"><a href="{url}">Source</a></p></article>'


def section(title, items):
    cards = "\n      ".join(card(i) for i in items[:5]) if items else '<p class="small">No qualifying items this run.</p>'
    return f'<h2>{html.escape(title)}</h2>\n      {cards}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue-id", required=True)
    args = ap.parse_args()

    q = json.loads((ROOT / "artifacts" / f"editorial_queue-{args.issue_id}.json").read_text(encoding="utf-8"))
    items = q.get("items", [])
    official = [i for i in items if "Official" in i.get("tags", [])]
    community = [i for i in items if "Community" in i.get("tags", [])]

    window_start = html.escape(q.get("window_start_utc", "unknown"))
    window_end = html.escape(q.get("window_end_utc", "unknown"))

    top_cards = "\n      ".join(card(i) for i in items[:5]) if items else '<p class="small">No qualifying items this run.</p>'

    body = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Issue {args.issue_id} — Microsoft Agentic AI Weekly</title>
  <link rel="stylesheet" href="../assets/styles.css" />
</head>
<body>
  <header class="site-header">
    <div class="container">
      <a class="brand" href="../index.html">Microsoft Agentic AI Weekly</a>
      <nav class="nav">
        <a href="../index.html">Home</a>
        <a href="../archive.html">Archive</a>
        <a href="../sources.html">Sources</a>
      </nav>
    </div>
  </header>
  <main>
    <div class="container content-shell">
      <article class="panel">
        <p class="kicker">Issue {args.issue_id}</p>
        <h1>Microsoft Agentic AI Weekly</h1>
        <p class="meta">Coverage window (UTC): {window_start} to {window_end} (end exclusive).</p>

        <h2>Top 5 you shouldn’t miss</h2>
        {top_cards}

        {section("Official updates", official)}
        {section("Community picks + creator spotlight", community)}

        <h2>Builder takeaway</h2>
        <p>Pick one item to apply this sprint, and ignore anything not tied to your current roadmap.</p>
      </article>
    </div>
  </main>
</body>
</html>
'''

    out = ROOT / "posts" / f"issue-{args.issue_id}.html"
    out.write_text(body, encoding="utf-8")
    print(str(out))


if __name__ == "__main__":
    main()
