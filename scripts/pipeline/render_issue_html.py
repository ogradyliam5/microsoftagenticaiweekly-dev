#!/usr/bin/env python3
import argparse
import datetime as dt
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SECTION_ORDER = ["Power Platform", "M365", "Microsoft Foundry", "Everything else"]


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
        (["rbac", "authentication"], "Practical security testing approach for auth and role boundaries."),
    ]
    for keys, text in rules:
        if all(k in title_l for k in keys):
            return text

    if custom and "potentially relevant update" not in custom.lower():
        return custom
    return f"{title} — useful if this is in your active delivery scope."


def assign_section(item):
    tags = set(item.get("tags", []))
    if "Power Platform" in tags:
        return "Power Platform"
    if "M365" in tags:
        return "M365"
    if "Foundry" in tags:
        return "Microsoft Foundry"
    return "Everything else"


def card(item):
    title = html.escape(item.get("title", "Untitled"))
    by = html.escape(speaker(item))
    summary = html.escape(concise_summary(item))
    url = html.escape(item.get("canonical_url", item.get("url", "#")))
    return f'<article class="signal-card"><h3>{title}</h3><p><strong>{by}:</strong> {summary}</p><p class="small"><a href="{url}">Source</a></p></article>'


def section(title, items):
    cards = "\n      ".join(card(i) for i in items) if items else '<p class="small">No qualifying items this run.</p>'
    return f'<h2>{html.escape(title)}</h2>\n      {cards}'


def format_human_date(iso_value):
    try:
        parsed = dt.datetime.fromisoformat(iso_value.replace("Z", "+00:00"))
        return parsed.strftime("%A, %d %B %Y")
    except Exception:
        return dt.datetime.utcnow().strftime("%A, %d %B %Y")


def issue_label(issue_id, generated_at):
    try:
        year, week = issue_id.split("-", 1)
        year_i = int(year)
        week_i = int(week)
        week_start = dt.date.fromisocalendar(year_i, week_i, 1)
        return f"Week of {week_start.strftime('%-d %b %Y')}"
    except Exception:
        return f"Edition {issue_id}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue-id", required=True)
    args = ap.parse_args()

    q = json.loads((ROOT / "artifacts" / f"editorial_queue-{args.issue_id}.json").read_text(encoding="utf-8"))
    items = q.get("items", [])

    unique_items = []
    seen_ids = set()
    for item in items:
        key = item.get("id") or item.get("canonical_url") or item.get("url") or item.get("title")
        if key in seen_ids:
            continue
        seen_ids.add(key)
        unique_items.append(item)

    sections = {name: [] for name in SECTION_ORDER}
    for item in unique_items:
        sections[assign_section(item)].append(item)

    window_start = html.escape(q.get("window_start_utc", "unknown"))
    window_end = html.escape(q.get("window_end_utc", "unknown"))
    publication_date = html.escape(format_human_date(q.get("generated_at", "")))
    label = html.escape(issue_label(args.issue_id, q.get("generated_at", "")))

    section_html = "\n\n        ".join(section(name, sections[name]) for name in SECTION_ORDER)

    body = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <script>
    (function () {{
      var key = 'maiw-theme';
      var theme = 'dark';
      try {{
        var stored = localStorage.getItem(key);
        if (stored === 'light' || stored === 'dark') {{
          theme = stored;
        }} else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {{
          theme = 'dark';
        }} else {{
          theme = 'light';
        }}
      }} catch (e) {{}}
      var root = document.documentElement;
      root.setAttribute('data-theme', theme);
      root.classList.remove('theme-dark', 'theme-light');
      root.classList.add(theme === 'dark' ? 'theme-dark' : 'theme-light');
      root.style.colorScheme = theme;
    }})();
  </script>
  <title>{label} — Microsoft Agentic AI Weekly</title>
  <link rel="stylesheet" href="../assets/legacy.css?v=20260305" />
</head>
<body>
  <header class="site-header">
    <div class="container">
      <a class="brand" href="../index.html">Microsoft Agentic AI Weekly</a>
      <nav class="nav">
        <button class="theme-toggle" type="button" data-theme-toggle aria-label="Toggle color mode">🌙 Dark</button>
        <a href="../index.html">Home</a>
        <a href="../archive.html">Archive</a>
        <a href="../about.html">Methodology</a>
      </nav>
    </div>
  </header>
  <main>
    <div class="container content-shell">
      <article class="panel">
        <p class="kicker">{label}</p>
        <h1>Microsoft Agentic AI Weekly</h1>
        <p class="meta">Published: {publication_date}</p>
        <p class="meta">Coverage window (UTC): {window_start} to {window_end} (end exclusive).</p>

        {section_html}

        <p>Pick one item to apply this sprint, and ignore anything not tied to your current roadmap.</p>
      </article>
    </div>
  </main>
  <script src="../assets/theme.js?v=20260304"></script>
</body>
</html>
'''

    out = ROOT / "posts" / f"issue-{args.issue_id}.html"
    out.write_text(body, encoding="utf-8")
    print(str(out))


if __name__ == "__main__":
    main()
