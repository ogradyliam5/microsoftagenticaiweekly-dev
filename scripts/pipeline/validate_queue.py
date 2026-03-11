#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib
import re
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]

REQUIRED_TOP_LEVEL_KEYS = {
    "contract_version",
    "issue_id",
    "generated_at",
    "window_start_utc",
    "window_end_utc",
    "items",
    "excluded",
    "mix_target",
    "mix_actual",
    "quality_summary",
    "composition",
}

REQUIRED_ITEM_KEYS = {
    "id",
    "title",
    "canonical_url",
    "publisher",
    "published_at_utc",
    "source_mix_bucket",
    "signal",
    "mini_abstract",
    "why_click",
    "confidence_label",
    "selection_reason",
    "score_total",
    "score_relevance",
    "score_quality",
    "score_freshness",
    "domain",
    "evidence",
}

BANNED_FILLER_PATTERNS = [
    "it still adds practical context",
    "use it to tighten",
    "use it to inform next-sprint priorities",
    "useful if this area is in your current delivery scope",
    "potentially relevant update",
]


class ValidationError(ValueError):
    pass


def fail(msg):
    raise ValidationError(msg)


def parse_utc(value, label):
    if not isinstance(value, str) or not value:
        fail(f"{label} must be a non-empty string")
    candidate = value.replace("Z", "+00:00")
    try:
        dt.datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValidationError(f"{label} must be ISO-8601: {value}") from exc


def sentence_count(value):
    parts = [s.strip() for s in re.split(r"[.!?]+", value or "") if s.strip()]
    return len(parts)


def has_banned_filler(value):
    value_l = (value or "").lower()
    return any(pattern in value_l for pattern in BANNED_FILLER_PATTERNS)


def validate_item(index, item):
    missing = sorted(REQUIRED_ITEM_KEYS - set(item.keys()))
    if missing:
        fail(f"Item {index} missing required keys: {', '.join(missing)}")

    if not item.get("title"):
        fail(f"Item {index} missing title")

    canonical = item.get("canonical_url")
    if not isinstance(canonical, str) or not canonical.startswith(("http://", "https://")):
        fail(f"Item {index} canonical_url must be absolute http(s)")

    parse_utc(item.get("published_at_utc"), f"Item {index} published_at_utc")

    mini = item.get("mini_abstract", "")
    why = item.get("why_click", "")

    if len(mini) > 280:
        fail(f"Item {index} mini_abstract exceeds 280 chars")
    if len(why) > 180:
        fail(f"Item {index} why_click exceeds 180 chars")

    if sentence_count(mini) > 2:
        fail(f"Item {index} mini_abstract must be <= 2 sentences")
    if sentence_count(why) > 1:
        fail(f"Item {index} why_click must be <= 1 sentence")

    if has_banned_filler(mini) or has_banned_filler(why):
        fail(f"Item {index} contains banned filler pattern")

    confidence = item.get("confidence_label")
    if confidence not in {"official", "reputable community", "early signal"}:
        fail(f"Item {index} invalid confidence_label: {confidence}")

    evidence = item.get("evidence") or []
    if not isinstance(evidence, list) or not evidence:
        fail(f"Item {index} evidence must be a non-empty list")
    for ev_idx, evidence_snippet in enumerate(evidence, start=1):
        if len((evidence_snippet or "").split()) > 25:
            fail(f"Item {index} evidence snippet {ev_idx} exceeds 25 words")


def validate_top_level(queue):
    missing = sorted(REQUIRED_TOP_LEVEL_KEYS - set(queue.keys()))
    if missing:
        fail(f"Queue missing required top-level keys: {', '.join(missing)}")

    if queue.get("contract_version") != "v2":
        fail("contract_version must be 'v2'")

    for field in ("generated_at", "window_start_utc", "window_end_utc"):
        parse_utc(queue.get(field), field)

    items = queue.get("items")
    excluded = queue.get("excluded")
    if not isinstance(items, list):
        fail("items must be an array")
    if not isinstance(excluded, list):
        fail("excluded must be an array")

    if not items:
        fail("No items in editorial queue")

    composition = queue.get("composition") or {}
    min_target = composition.get("target_min_items")
    max_target = composition.get("target_max_items")
    selected_count = composition.get("selected_count")

    if not isinstance(min_target, int) or not isinstance(max_target, int):
        fail("composition target_min_items/target_max_items must be integers")
    if not isinstance(selected_count, int):
        fail("composition.selected_count must be an integer")

    if selected_count != len(items):
        fail("composition.selected_count must match len(items)")

    override = composition.get("override")
    override_enabled = isinstance(override, dict) and override.get("enabled") is True

    if not (min_target <= len(items) <= max_target) and not override_enabled:
        fail(
            f"Selected item count {len(items)} is outside target range {min_target}-{max_target} without explicit composition override"
        )


def validate_domain_and_duplicates(items, queue):
    canonical_urls = [item["canonical_url"].strip().lower() for item in items]
    if len(canonical_urls) != len(set(canonical_urls)):
        fail("Duplicate canonical_url values found in selected items")

    domains = [item.get("domain", "unknown") for item in items]
    domain_counts = Counter(domains)

    domain_cap = (queue.get("quality_summary") or {}).get("domain_cap", 2)
    composition_override = (queue.get("composition") or {}).get("override")
    override_enabled = isinstance(composition_override, dict) and composition_override.get("enabled") is True

    exceeded = {domain: count for domain, count in domain_counts.items() if count > domain_cap}
    if exceeded and not override_enabled:
        fail(f"Domain concentration cap exceeded: {exceeded} (cap {domain_cap})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-id", required=True)
    args = parser.parse_args()

    queue_path = ROOT / "artifacts" / f"editorial_queue-{args.issue_id}.json"
    if not queue_path.exists():
        print(f"VALIDATION_ERROR: Missing queue file: {queue_path}")
        sys.exit(1)

    try:
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        validate_top_level(queue)

        items = queue.get("items", [])
        for idx, item in enumerate(items, start=1):
            validate_item(idx, item)

        validate_domain_and_duplicates(items, queue)

    except ValidationError as exc:
        print(f"VALIDATION_ERROR: {exc}")
        sys.exit(1)

    print(f"Validation OK: {len(queue.get('items', []))} items (contract v2)")


if __name__ == "__main__":
    main()
