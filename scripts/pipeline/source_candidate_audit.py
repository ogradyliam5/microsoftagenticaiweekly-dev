#!/usr/bin/env python3
"""Audit candidate/rejected source feed health for approval-ready source hygiene."""

from __future__ import annotations

import argparse
import json
import ssl
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "microsoftagenticaiweekly-source-audit/1.0"
TIMEOUT_SECONDS = 15
INGESTABILITY_REASONS = ["machine_ingestable", "no_items", "unsupported_root_tag", "fetch_failed", "unknown"]


def _reason_percentages(counter: dict[str, int], total: int) -> dict[str, float]:
    if total <= 0:
        return {reason: 0.0 for reason in INGESTABILITY_REASONS}
    return {reason: round((counter.get(reason, 0) / total) * 100, 1) for reason in INGESTABILITY_REASONS}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _local_name(tag: str | None) -> str:
    if not tag:
        return ""
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _looks_machine_ingestable(root_tag: str | None, item_count: int) -> bool:
    if item_count <= 0:
        return False
    return _local_name(root_tag) in {"rss", "RDF", "feed"}


def _ingestability_reason(ok: bool, root_tag: str | None, item_count: int, machine_ingestable: bool) -> str:
    if not ok:
        return "fetch_failed"
    if machine_ingestable:
        return "machine_ingestable"
    if item_count <= 0:
        return "no_items"
    if _local_name(root_tag) not in {"rss", "RDF", "feed"}:
        return "unsupported_root_tag"
    return "unknown"


def _empty_reason_counter() -> dict[str, int]:
    return {reason: 0 for reason in INGESTABILITY_REASONS}


def _bump_reason(counter: dict[str, int], reason: str | None) -> None:
    normalized = reason if reason in counter else "unknown"
    counter[normalized] += 1


def fetch_feed_status(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.1",
        },
    )
    ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS, context=ctx) as resp:
            content = resp.read(1_000_000)
            status_code = getattr(resp, "status", 200)
            final_url = resp.geturl()
            content_type = resp.headers.get("Content-Type", "")

        root = ET.fromstring(content)
        items = root.findall(".//item")
        entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")
        item_count = len(items) + len(entries)
        root_tag = _local_name(root.tag)
        machine_ingestable = _looks_machine_ingestable(root.tag, item_count)

        return {
            "ok": True,
            "status_code": status_code,
            "content_type": content_type,
            "final_url": final_url,
            "root_tag": root_tag,
            "item_count": item_count,
            "machine_ingestable": machine_ingestable,
            "ingestability_reason": _ingestability_reason(True, root_tag, item_count, machine_ingestable),
            "error": None,
        }
    except urllib.error.HTTPError as e:
        return {
            "ok": False,
            "status_code": e.code,
            "content_type": None,
            "final_url": url,
            "root_tag": None,
            "item_count": 0,
            "machine_ingestable": False,
            "ingestability_reason": _ingestability_reason(False, None, 0, False),
            "error": f"HTTP {e.code}: {e.reason}",
        }
    except (urllib.error.URLError, TimeoutError, ET.ParseError, ssl.SSLError, ValueError) as e:
        return {
            "ok": False,
            "status_code": None,
            "content_type": None,
            "final_url": url,
            "root_tag": None,
            "item_count": 0,
            "machine_ingestable": False,
            "ingestability_reason": _ingestability_reason(False, None, 0, False),
            "error": str(e),
        }


def audit_sources(sources_path: Path) -> dict:
    raw = json.loads(sources_path.read_text(encoding="utf-8"))
    candidates = raw.get("candidates", {})

    results = {
        "generated_at": now_iso(),
        "sources_path": str(sources_path),
        "candidate_add": [],
        "candidate_reject": [],
        "summary": {
            "candidate_add_ok": 0,
            "candidate_add_failed": 0,
            "candidate_add_non_ingestable": 0,
            "candidate_add_non_ingestable_no_items": 0,
            "candidate_add_non_ingestable_unsupported_root": 0,
            "candidate_reject_still_blocked": 0,
            "candidate_reject_now_ok": 0,
            "candidate_reject_now_ingestable": 0,
            "candidate_reject_now_non_ingestable": 0,
            "candidate_add_reason_counts": _empty_reason_counter(),
            "candidate_reject_reason_counts": _empty_reason_counter(),
        },
    }

    for item in candidates.get("add", []):
        status = fetch_feed_status(item["url"])
        row = {"id": item["id"], "name": item.get("name", item["id"]), "url": item["url"], **status}
        results["candidate_add"].append(row)
        _bump_reason(results["summary"]["candidate_add_reason_counts"], status.get("ingestability_reason"))
        if status["ok"]:
            results["summary"]["candidate_add_ok"] += 1
            if not status["machine_ingestable"]:
                results["summary"]["candidate_add_non_ingestable"] += 1
                reason = status.get("ingestability_reason")
                if reason == "no_items":
                    results["summary"]["candidate_add_non_ingestable_no_items"] += 1
                elif reason == "unsupported_root_tag":
                    results["summary"]["candidate_add_non_ingestable_unsupported_root"] += 1
        else:
            results["summary"]["candidate_add_failed"] += 1

    for item in candidates.get("reject", []):
        status = fetch_feed_status(item["url"])
        row = {"id": item["id"], "url": item["url"], "expected_reject_reason": item.get("reason", ""), **status}
        results["candidate_reject"].append(row)
        _bump_reason(results["summary"]["candidate_reject_reason_counts"], status.get("ingestability_reason"))
        if status["ok"]:
            results["summary"]["candidate_reject_now_ok"] += 1
            if status["machine_ingestable"]:
                results["summary"]["candidate_reject_now_ingestable"] += 1
            else:
                results["summary"]["candidate_reject_now_non_ingestable"] += 1
        else:
            results["summary"]["candidate_reject_still_blocked"] += 1

    results["summary"]["candidate_add_reason_percentages"] = _reason_percentages(
        results["summary"]["candidate_add_reason_counts"],
        len(results["candidate_add"]),
    )
    results["summary"]["candidate_reject_reason_percentages"] = _reason_percentages(
        results["summary"]["candidate_reject_reason_counts"],
        len(results["candidate_reject"]),
    )

    return results


def write_markdown_report(report: dict, path: Path) -> None:
    lines = []
    lines.append("# Source Candidate Audit Report")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append("")

    s = report["summary"]
    lines.append("## Summary")
    lines.append(f"- Candidate add feeds healthy: {s['candidate_add_ok']}")
    lines.append(f"- Candidate add feeds failing: {s['candidate_add_failed']}")
    lines.append(f"- Candidate add feeds non-ingestable: {s['candidate_add_non_ingestable']}")
    lines.append(f"  - due to no items: {s['candidate_add_non_ingestable_no_items']}")
    lines.append(f"  - due to unsupported root tag: {s['candidate_add_non_ingestable_unsupported_root']}")
    lines.append(f"- Rejected feeds still blocked: {s['candidate_reject_still_blocked']}")
    lines.append(f"- Rejected feeds now healthy (review needed): {s['candidate_reject_now_ok']}")
    lines.append(f"- Rejected feeds now machine-ingestable (promotion candidates): {s['candidate_reject_now_ingestable']}")
    lines.append(f"- Rejected feeds now healthy but non-ingestable: {s['candidate_reject_now_non_ingestable']}")
    lines.append("")

    lines.append("## Ingestability reason breakdown")
    lines.append("- Candidate add")
    for reason, count in s["candidate_add_reason_counts"].items():
        percent = s.get("candidate_add_reason_percentages", {}).get(reason, 0.0)
        lines.append(f"  - {reason}: {count} ({percent:.1f}%)")
    lines.append("- Candidate reject")
    for reason, count in s["candidate_reject_reason_counts"].items():
        percent = s.get("candidate_reject_reason_percentages", {}).get(reason, 0.0)
        lines.append(f"  - {reason}: {count} ({percent:.1f}%)")
    lines.append("")

    lines.append("## Candidate Add Feed Checks")
    for row in report["candidate_add"]:
        status = "OK" if row["ok"] else "FAIL"
        details = f"HTTP {row['status_code']}" if row["status_code"] else row["error"]
        ingestable = "ingestable" if row["machine_ingestable"] else "non-ingestable"
        lines.append(
            f"- `{row['id']}` — {status} — {details} — root: {row.get('root_tag') or 'n/a'} — items: {row['item_count']} — {ingestable} — reason: {row.get('ingestability_reason', 'n/a')}"
        )
    lines.append("")

    lines.append("## Rejected Feed Re-check")
    for row in report["candidate_reject"]:
        status = "NOW_OK" if row["ok"] else "STILL_BLOCKED"
        details = f"HTTP {row['status_code']}" if row["status_code"] else row["error"]
        ingestable = "ingestable" if row["machine_ingestable"] else "non-ingestable"
        lines.append(
            f"- `{row['id']}` — {status} — {details} — root: {row.get('root_tag') or 'n/a'} — items: {row['item_count']} — {ingestable} — reason: {row.get('ingestability_reason', 'n/a')}"
        )
    lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit source candidate feed health")
    parser.add_argument("--sources", default="data/sources.json", help="Path to sources JSON")
    parser.add_argument("--out-json", default="artifacts/source_candidate_audit.json", help="Output JSON path")
    parser.add_argument("--out-md", default="artifacts/source_candidate_audit.md", help="Output markdown report path")
    args = parser.parse_args()

    sources_path = Path(args.sources)
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)

    report = audit_sources(sources_path)

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_markdown_report(report, out_md)

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
