#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]


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
        (["roadmap", "spfx"], "Signals near-term platform changes likely to affect planning and maintenance."),
        (["power pages", "webapi"], "Highlights a practical workaround for Power Pages permission constraints."),
        (["agent framework", "semantic kernel", "autogen"], "Useful migration guidance for teams moving to Microsoft Agent Framework."),
        (["rbac", "authentication"], "Practical security testing guidance for auth and role-boundary validation."),
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


def section(items, label, limit=5):
    out = [f"## {label}", ""]
    if not items:
        return out + ["No qualifying items this run.", ""]
    for it in items[:limit]:
        out += [f"### {it['title']}", narrative_line(it), ""]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue-id", required=True)
    args = ap.parse_args()

    queue_path = ROOT / "artifacts" / f"editorial_queue-{args.issue_id}.json"
    q = json.loads(queue_path.read_text(encoding="utf-8"))
    items = q.get("items", [])

    pp = [i for i in items if "Power Platform" in i.get("tags", [])]
    m365 = [i for i in items if "M365" in i.get("tags", [])]
    foundry = [i for i in items if "Foundry" in i.get("tags", [])]
    official = [i for i in items if "Official" in i.get("tags", [])]
    community = [i for i in items if "Community" in i.get("tags", [])]

    window_start = q.get("window_start_utc", "unknown")
    window_end = q.get("window_end_utc", "unknown")

    post = [
        f"# Microsoft Agentic AI Weekly — Issue {args.issue_id}",
        "",
        f"_Generated on {dt.datetime.utcnow().date().isoformat()} · Coverage window (UTC): {window_start} to {window_end} (end exclusive). Requires human editorial approval before publishing._",
        "",
        "## What changed this week",
        "",
        "Fast scan of updates published in last week’s window that can affect active Microsoft agent delivery work.",
        "",
        "## Top 5 you shouldn’t miss",
        "",
    ]

    if not items:
        post += ["No qualifying items this run.", ""]
    else:
        for idx, it in enumerate(items[:5], start=1):
            post += [f"{idx}. **{it['title']}**", narrative_line(it), ""]

    post += section(official, "Official updates")
    post += section(pp, "Power Platform")
    post += section(m365, "M365")
    post += section(foundry, "Foundry")
    post += section(community, "Community picks + creator spotlight")

    post += [
        "## Builder takeaway",
        "",
        "Pick one item to apply this sprint, and ignore anything not tied to your current roadmap.",
        "",
        "## Corrections",
        "",
        "If you spot an error or context miss, email [ogradyliam5@gmail.com](mailto:ogradyliam5@gmail.com?subject=Correction%20request).",
        "",
    ]

    email = [
        f"# Microsoft Agentic AI Weekly — Issue {args.issue_id}",
        "",
        "Draft only. Do not send without Liam approval.",
        f"Coverage window (UTC): {window_start} to {window_end} (end exclusive).",
        "",
        "## Top 5 you shouldn’t miss",
        "",
    ]

    if not items:
        email += ["No qualifying items this run."]
    else:
        for it in items[:5]:
            email.append(f"- **{it['title']}**")
            email.append(f"  {narrative_line(it).lstrip('- ')}")

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
