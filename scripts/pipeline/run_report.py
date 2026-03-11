#!/usr/bin/env python3
"""Generate weekly run analytics report from queue + curation manifest + run summary."""

import argparse
import datetime as dt
import json
import pathlib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def issue_id_today():
    now = dt.datetime.now(dt.timezone.utc)
    year, week, _ = now.isocalendar()
    return f"{year}-{week:02d}"


def fmt_counter(counter: Counter):
    if not counter:
        return "- none"
    return "\n".join(f"- {key}: {value}" for key, value in counter.most_common())


def generate(issue_id: str) -> pathlib.Path:
    queue_path = ART / f"editorial_queue-{issue_id}.json"
    manifest_path = ART / f"curation_manifest-{issue_id}.json"
    run_path = ART / "last_run.json"

    queue = load_json(queue_path)
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    run = load_json(run_path) if run_path.exists() else {}

    items = queue.get("items", [])
    quality_summary = queue.get("quality_summary", {})

    by_area = Counter(item.get("product_area", "unknown") for item in items)
    by_bucket = Counter(item.get("source_mix_bucket", "unknown") for item in items)
    by_confidence = Counter(item.get("confidence_label", "unknown") for item in items)
    by_domain = Counter(item.get("domain", "unknown") for item in items)

    top_items = sorted(items, key=lambda item: item.get("score_total", 0), reverse=True)[:5]

    exclusion_counts = manifest.get("reason_counts", {})
    if exclusion_counts:
        exclusion_counter = Counter(exclusion_counts)
    else:
        exclusion_counter = Counter(row.get("reason_code", "unknown") for row in queue.get("excluded", []))

    lines = [
        f"# Weekly Pipeline Run Report - {issue_id}",
        "",
        f"Generated: {dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')}",
        "",
        "## Run status",
        f"- Pipeline status: {run.get('pipeline_status', 'unknown')}",
        f"- Buttondown: {run.get('buttondown', 'unknown')}",
        f"- Queue file: `{queue_path.relative_to(ROOT)}`",
        f"- Curation manifest: `{manifest_path.relative_to(ROOT)}`" if manifest_path.exists() else "- Curation manifest: not found",
        f"- Last run file: `{run_path.relative_to(ROOT)}`" if run_path.exists() else "- Last run file: not found",
        "",
        "## Contract and composition",
        f"- Queue contract version: {queue.get('contract_version', 'unknown')}",
        f"- Selected items: {len(items)}",
        f"- Target range: {queue.get('composition', {}).get('target_min_items', 'n/a')} to {queue.get('composition', {}).get('target_max_items', 'n/a')}",
        f"- Composition override: {queue.get('composition', {}).get('override')}",
        "",
        "## Quality gates",
        f"- Duplicate rejections: {quality_summary.get('duplicate_rejections', 0)}",
        f"- Blandness rejections: {quality_summary.get('blandness_rejections', 0)}",
        f"- Low relevance rejections: {quality_summary.get('low_relevance_rejections', 0)}",
        f"- Domain cap: {quality_summary.get('domain_cap', 'n/a')}",
        f"- Unique selected domains: {quality_summary.get('selected_unique_domains', 0)}",
        f"- Top domain share percent: {quality_summary.get('top_domain_share_percent', 0)}",
        "",
        "## Output mix",
        f"- Official count: {queue.get('mix_actual', {}).get('official_count', 0)}",
        f"- Independent count: {queue.get('mix_actual', {}).get('independent_count', 0)}",
        "",
        "### By product area",
        fmt_counter(by_area),
        "",
        "### By source bucket",
        fmt_counter(by_bucket),
        "",
        "### By confidence label",
        fmt_counter(by_confidence),
        "",
        "### By selected domain",
        fmt_counter(by_domain),
        "",
        "## Exclusion reasons",
        fmt_counter(exclusion_counter),
        "",
        "## Top scored items",
    ]

    if not top_items:
        lines.append("- none")
    else:
        for index, item in enumerate(top_items, start=1):
            title = item.get("title", "(untitled)")
            score = item.get("score_total", 0)
            lines.append(f"{index}. {title} ({score:.4f})")
            lines.append(f"   - Domain: {item.get('domain', 'unknown')}")
            lines.append(f"   - Confidence: {item.get('confidence_label', 'unknown')}")
            lines.append(f"   - URL: {item.get('canonical_url') or item.get('url') or ''}")

    out_path = ART / f"run_report-{issue_id}.md"
    out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-id", help="Override ISO week issue id (YYYY-WW).")
    args = parser.parse_args()

    issue_id = args.issue_id or issue_id_today()
    out = generate(issue_id)
    print(json.dumps({"issue_id": issue_id, "report": str(out.relative_to(ROOT))}, indent=2))
