#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]


def text(v):
    return (v or "").strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:80]


def fetch_rss(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def parse_feed(source, raw):
    out = []
    root = ET.fromstring(raw)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    if root.tag.endswith("feed"):
        entries = root.findall("atom:entry", ns)
        for e in entries[:12]:
            title = text(e.findtext("atom:title", default="", namespaces=ns))
            link_el = e.find("atom:link", ns)
            link = link_el.attrib.get("href", "") if link_el is not None else ""
            pub = text(e.findtext("atom:updated", default="", namespaces=ns))
            out.append((title, link, pub))
    else:
        for i in root.findall("./channel/item")[:12]:
            title = text(i.findtext("title", default=""))
            link = text(i.findtext("link", default=""))
            pub = text(i.findtext("pubDate", default=""))
            out.append((title, link, pub))
    return out


def classify(title, source_area):
    t = title.lower()
    tags = []
    if source_area == "Power Platform" or any(k in t for k in ["copilot studio", "power automate", "power apps", "dataverse"]):
        tags.append("Power Platform")
    if source_area == "M365" or any(k in t for k in ["microsoft 365", "teams", "graph"]):
        tags.append("M365")
    if source_area == "Foundry" or any(k in t for k in ["azure ai", "foundry", "agent", "model"]):
        tags.append("Foundry")
    return tags or [source_area]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue-id", required=True)
    args = ap.parse_args()

    sources = json.loads((ROOT / "data/sources.json").read_text(encoding="utf-8"))["sources"]
    items, excluded = [], []
    seen = set()

    for s in sources:
        if s["type"] not in {"rss", "github"}:
            excluded.append({"source": s["id"], "reason": "manual/non-fetch source"})
            continue
        try:
            raw = fetch_rss(s["url"])
            for title, link, pub in parse_feed(s, raw):
                if not title or not link:
                    continue
                key = slug(title)
                if key in seen:
                    excluded.append({"url": link, "reason": "duplicate_title"})
                    continue
                seen.add(key)
                confidence = "High" if s.get("trust") == "official" else "Medium"
                tags = classify(title, s.get("product_area", "Mixed"))
                items.append({
                    "id": key,
                    "title": title,
                    "url": link,
                    "canonical_url": link,
                    "author": "",
                    "publisher": s["name"],
                    "published_at": pub or dt.datetime.utcnow().isoformat() + "Z",
                    "fetched_at": dt.datetime.utcnow().isoformat() + "Z",
                    "product_area": s.get("product_area", "Mixed"),
                    "source_type": s["type"],
                    "summary_bullets": ["Auto-collected candidate. Editorial rewrite required before publishing."],
                    "why_it_matters": "Potentially relevant update for Microsoft Agentic AI builders.",
                    "audience": "Dev",
                    "effort": "TBD during editorial review",
                    "confidence": confidence,
                    "tags": tags + (["Official"] if confidence == "High" else ["Community"]),
                    "evidence": [f"Source title: {title[:90]}"]
                })
        except Exception as e:
            excluded.append({"source": s["id"], "reason": f"fetch_error: {e}"})

    items = sorted(items, key=lambda x: (x["confidence"] != "High", x["publisher"], x["title"]))
    top = items[:24]

    queue = {
        "issue_id": args.issue_id,
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "items": top,
        "clusters": [],
        "excluded": excluded,
        "questions_for_liam": [
            "Any sources to add/remove this week? (approval required)",
            "Any item titles that should be down-ranked as noise?"
        ]
    }

    art = ROOT / "artifacts"
    art.mkdir(exist_ok=True)
    q_json = art / f"editorial_queue-{args.issue_id}.json"
    q_md = art / f"editorial_queue-{args.issue_id}.md"
    q_json.write_text(json.dumps(queue, indent=2), encoding="utf-8")

    lines = [
        f"# Weekly Editorial Queue — {args.issue_id}",
        "",
        f"Generated: {queue['generated_at']}",
        f"Total included: {len(top)}",
        f"Excluded: {len(excluded)}",
        "",
        "## Top candidates",
        ""
    ]
    for i, it in enumerate(top[:15], start=1):
        lines += [
            f"{i}. **{it['title']}**",
            f"   - Publisher: {it['publisher']}",
            f"   - Confidence: {it['confidence']}",
            f"   - URL: {it['canonical_url']}",
        ]
    lines += ["", "## Questions for Liam", ""] + [f"- {q}" for q in queue["questions_for_liam"]]
    q_md.write_text("\n".join(lines), encoding="utf-8")
    print(str(q_json))
    print(str(q_md))


if __name__ == "__main__":
    main()
