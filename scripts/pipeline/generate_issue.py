#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SECTION_ORDER = ["Power Platform", "M365", "Microsoft Foundry", "Everything else"]


def issue_label(issue_id):
    try:
        year, week = issue_id.split("-", 1)
        monday = dt.date.fromisocalendar(int(year), int(week), 1)
        return f"Week of {monday.day} {monday.strftime('%b %Y')}"
    except Exception:
        return f"Edition {issue_id}"


def format_human_date(iso_value):
    if not iso_value:
        return dt.datetime.now(dt.timezone.utc).strftime("%A, %d %B %Y")
    try:
        parsed = dt.datetime.fromisoformat(iso_value.replace("Z", "+00:00"))
        return parsed.strftime("%A, %d %B %Y")
    except Exception:
        return dt.datetime.now(dt.timezone.utc).strftime("%A, %d %B %Y")


def assign_section(item):
    tags = set(item.get("tags", []))
    if "Power Platform" in tags:
        return "Power Platform"
    if "M365" in tags:
        return "M365"
    if "Foundry" in tags:
        return "Microsoft Foundry"
    return "Everything else"


def canonical_story_lines(item):
    url = item.get("canonical_url") or item.get("url") or "#"
    publisher = item.get("publisher") or "Unknown"
    signal = item.get("signal") or item.get("title") or ""
    mini = item.get("mini_abstract") or ""
    why = item.get("why_click") or ""
    confidence = item.get("confidence_label") or "unknown"

    return [
        f"- Signal: {signal}",
        f"- Mini-abstract: {mini}",
        f"- Why click: {why}",
        f"- Source confidence: {confidence}",
        f"- Source: [{publisher}]({url})",
    ]


def section_block(section_name, items):
    lines = [f"## {section_name}", ""]
    if not items:
        lines.extend(["No qualifying items this run.", ""])
        return lines

    for item in items:
        lines.append(f"### {item.get('title', 'Untitled')}")
        lines.extend(canonical_story_lines(item))
        lines.append("")
    return lines


def build_executive_summary(items):
    if not items:
        return ["- No qualifying signals selected this run."]

    top = sorted(items, key=lambda x: x.get("score_total", 0), reverse=True)[:3]
    summary = []
    for item in top:
        title = item.get("title", "Untitled")
        why = item.get("why_click", "")
        summary.append(f"- {title}: {why}")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-id", required=True)
    args = parser.parse_args()

    queue_path = ROOT / "artifacts" / f"editorial_queue-{args.issue_id}.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))

    items = queue.get("items", [])

    # de-dupe safety by canonical URL
    unique_items = []
    seen = set()
    for item in items:
        key = (item.get("canonical_url") or item.get("title") or "").strip().lower()
        if key in seen:
            continue
        seen.add(key)
        unique_items.append(item)

    sections = {name: [] for name in SECTION_ORDER}
    for item in unique_items:
        sections[assign_section(item)].append(item)

    label = issue_label(args.issue_id)
    generated_at = queue.get("generated_at", "")
    published_date = format_human_date(generated_at)
    window_start = queue.get("window_start_utc", "unknown")
    window_end = queue.get("window_end_utc", "unknown")

    post_lines = [
        f"# Microsoft Agentic AI Weekly - {label}",
        "",
        f"_Published: {published_date}. Requires human editorial approval before publishing._",
        "",
        f"Coverage window (UTC): {window_start} to {window_end} (end exclusive)",
        "",
        "## Executive summary",
    ]
    post_lines.extend(build_executive_summary(unique_items))
    post_lines.append("")

    for section_name in SECTION_ORDER:
        post_lines.extend(section_block(section_name, sections[section_name]))

    post_lines.extend([
        "This edition follows the canonical story unit: signal, mini-abstract, why-click, and source confidence.",
        "",
        "If you spot an error or context miss, email [ogradyliam5@gmail.com](mailto:ogradyliam5@gmail.com?subject=Correction%20request).",
        "",
    ])

    email_lines = [
        f"# Microsoft Agentic AI Weekly - {label}",
        "",
        "Draft only. Do not send without Liam approval.",
        f"Published: {published_date}",
        f"Coverage window (UTC): {window_start} to {window_end} (end exclusive)",
        "",
        "## Executive summary",
    ]
    email_lines.extend(build_executive_summary(unique_items))
    email_lines.append("")

    for section_name in SECTION_ORDER:
        email_lines.append(f"## {section_name}")
        email_lines.append("")
        if not sections[section_name]:
            email_lines.extend(["No qualifying items this run.", ""])
            continue

        for item in sections[section_name]:
            email_lines.append(f"- **{item.get('title', 'Untitled')}**")
            email_lines.append(f"  Signal: {item.get('signal', '')}")
            email_lines.append(f"  Mini-abstract: {item.get('mini_abstract', '')}")
            email_lines.append(f"  Why click: {item.get('why_click', '')}")
            email_lines.append(f"  Source confidence: {item.get('confidence_label', 'unknown')}")
            email_lines.append(f"  Source: {item.get('canonical_url') or item.get('url') or '#'}")
            email_lines.append("")

    posts_dir = ROOT / "posts"
    drafts_dir = ROOT / "drafts"
    posts_dir.mkdir(exist_ok=True)
    drafts_dir.mkdir(exist_ok=True)

    post_path = posts_dir / f"issue-{args.issue_id}.md"
    email_path = drafts_dir / f"email-{args.issue_id}.md"

    post_path.write_text("\n".join(post_lines), encoding="utf-8")
    email_path.write_text("\n".join(email_lines), encoding="utf-8")

    print(str(post_path))
    print(str(email_path))


if __name__ == "__main__":
    main()
