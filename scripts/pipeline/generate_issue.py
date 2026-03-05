#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib
import re

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

    heuristics = [
        (["copilot studio", "mcp"], "Shows a concrete Copilot Studio build pattern you can reuse quickly."),
        (["dataverse", "search"], "Improves retrieval quality for Dataverse-grounded copilots."),
        (["agent framework", "semantic kernel", "autogen"], "Useful migration guidance for teams moving to Microsoft Agent Framework."),
        (["rbac", "authentication"], "Practical security testing guidance for auth and role-boundary validation."),
        (["governance"], "Useful governance pattern for safer AI workload delivery and scale."),
    ]

    for keys, text in heuristics:
        if all(k in title_l for k in keys):
            return text

    if custom and "potentially relevant update" not in custom.lower():
        return custom

    trimmed = re.sub(r"\s+", " ", title).strip(" .")
    return f"{trimmed} — useful if this area is in your current delivery scope."


def narrative_line(item):
    who = speaker(item)
    why = concise_summary(item)
    url = item.get("canonical_url", item.get("url", "#"))
    return f"- **{who}:** {why} [Read source]({url})"


def assign_section(item):
    tags = set(item.get("tags", []))
    if "Power Platform" in tags:
        return "Power Platform"
    if "M365" in tags:
        return "M365"
    if "Foundry" in tags:
        return "Microsoft Foundry"
    return "Everything else"


def section(label, items):
    out = [f"## {label}", ""]
    if not items:
        return out + ["No qualifying items this run.", ""]
    for it in items:
        out += [f"### {it['title']}", narrative_line(it), ""]
    return out


def format_human_date(iso_value):
    try:
        parsed = dt.datetime.fromisoformat(iso_value.replace("Z", "+00:00"))
        return parsed.strftime("%A, %d %B %Y")
    except Exception:
        return dt.datetime.utcnow().strftime("%A, %d %B %Y")


def issue_label(issue_id):
    try:
        y, w = issue_id.split('-', 1)
        week_start = dt.date.fromisocalendar(int(y), int(w), 1)
        return f"Week of {week_start.strftime('%-d %b %Y')}"
    except Exception:
        return f"Edition {issue_id}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue-id", required=True)
    args = ap.parse_args()

    queue_path = ROOT / "artifacts" / f"editorial_queue-{args.issue_id}.json"
    q = json.loads(queue_path.read_text(encoding="utf-8"))
    items = q.get("items", [])

    seen_ids = set()
    unique_items = []
    for item in items:
        key = item.get("id") or item.get("canonical_url") or item.get("url") or item.get("title")
        if key in seen_ids:
            continue
        seen_ids.add(key)
        unique_items.append(item)

    sections = {name: [] for name in SECTION_ORDER}
    for item in unique_items:
        sections[assign_section(item)].append(item)

    window_start = q.get("window_start_utc", "unknown")
    window_end = q.get("window_end_utc", "unknown")
    publication_date = format_human_date(q.get("generated_at", ""))

    label = issue_label(args.issue_id)

    post = [
        f"# Microsoft Agentic AI Weekly — {label}",
        "",
        f"_Published: {publication_date} · Coverage window (UTC): {window_start} to {window_end} (end exclusive). Requires human editorial approval before publishing._",
        "",
        "Single weekly digest focused on high-signal agentic AI updates for Microsoft builders.",
        "",
    ]

    for section_name in SECTION_ORDER:
        post += section(section_name, sections[section_name])

    post += [
        "",
        "Pick one item to apply this sprint, and ignore anything not tied to your current roadmap.",
        "",
        "If you spot an error or context miss, email [ogradyliam5@gmail.com](mailto:ogradyliam5@gmail.com?subject=Correction%20request).",
        "",
    ]

    email = [
        f"# Microsoft Agentic AI Weekly — {label}",
        "",
        "Draft only. Do not send without Liam approval.",
        f"Published: {publication_date}",
        f"Coverage window (UTC): {window_start} to {window_end} (end exclusive).",
        "",
    ]

    for section_name in SECTION_ORDER:
        email += [f"## {section_name}", ""]
        if not sections[section_name]:
            email += ["No qualifying items this run.", ""]
            continue
        for item in sections[section_name]:
            email.append(f"- **{item['title']}**")
            email.append(f"  {narrative_line(item).lstrip('- ')}")
        email.append("")

    posts = ROOT / "posts"
    drafts = ROOT / "drafts"
    posts.mkdir(exist_ok=True)
    drafts.mkdir(exist_ok=True)

    (posts / f"issue-{args.issue_id}.md").write_text("\n".join(post), encoding="utf-8")
    (drafts / f"email-{args.issue_id}.md").write_text("\n".join(email), encoding="utf-8")
    print(str(posts / f"issue-{args.issue_id}.md"))
    print(str(drafts / f"email-{args.issue_id}.md"))


if __name__ == "__main__":
    main()
