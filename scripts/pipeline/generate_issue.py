#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]


def section(items, label):
    out = [f"## {label}", ""]
    if not items:
        return out + ["No qualifying items this run.", ""]
    for it in items[:5]:
        out += [
            f"### {it['title']}",
            f"- Why it matters: {it['why_it_matters']}",
            f"- Who it’s for: {it['audience']}",
            f"- Effort / prereqs: {it['effort']}",
            f"- Confidence: {it['confidence']}",
            f"- Source: [{it['publisher']}]({it['canonical_url']})",
            ""
        ]
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

    post = [
        f"# Microsoft Agentic AI Weekly — Issue {args.issue_id}",
        "",
        f"_Generated draft on {dt.datetime.utcnow().date().isoformat()} (requires human editorial approval before publishing)._",
        "",
        "## Top 5 you shouldn’t miss",
        "",
    ]
    for it in items[:5]:
        post += [f"- **{it['title']}** — {it['why_it_matters']} ([source]({it['canonical_url']}))"]

    post += [""]
    post += section([i for i in items if "Official" in i.get("tags", [])], "Official updates")
    post += section(pp, "Power Platform")
    post += section(m365, "M365")
    post += section(foundry, "Foundry")
    post += section([i for i in items if "Community" in i.get("tags", [])], "Community picks + creator spotlight")

    post += [
        "## Corrections",
        "",
        "If you spot an error or context miss, email [ogradyliam5@gmail.com](mailto:ogradyliam5@gmail.com?subject=Correction%20request).",
        ""
    ]

    email = [
        f"# Microsoft Agentic AI Weekly — Issue {args.issue_id}",
        "",
        "Draft only. Do not send without Liam approval.",
        "",
        "Top 5 you shouldn’t miss:",
    ]
    for it in items[:5]:
        email += [f"- {it['title']} ({it['canonical_url']})"]

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
