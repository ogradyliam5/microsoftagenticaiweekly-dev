#!/usr/bin/env python3
"""Audit candidate/rejected source feed health for approval-ready source hygiene."""

from __future__ import annotations

import argparse
import json
import ssl
import urllib.error
import urllib.request
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "microsoftagenticaiweekly-source-audit/1.0"
TIMEOUT_SECONDS = 15
INGESTABILITY_REASONS = ["machine_ingestable", "no_items", "unsupported_root_tag", "fetch_failed", "unknown"]
NON_INGESTABLE_REASON_PRIORITY = ["fetch_failed", "no_items", "unsupported_root_tag", "unknown"]
PROMOTION_QUEUE_PRIORITY = ["candidate_add", "candidate_reject"]
POLICY_BLOCK_TYPE_PRIORITY = [
    "publication_noise",
    "topic_noise",
    "community_forum",
    "stale_or_low_signal",
    "manual_review_hold",
    "other_policy",
]


def _policy_block_type(reason: str | None) -> str:
    text = (reason or "").strip().lower()
    if not text:
        return "other_policy"
    if "tag aggregator" in text or "publication feed" in text:
        return "publication_noise"
    if "topical" in text or "precision" in text or "topic" in text or "noise" in text:
        return "topic_noise"
    if "forum" in text or "board" in text or "discussion-heavy" in text:
        return "community_forum"
    if "stale cadence" in text or "low-signal" in text:
        return "stale_or_low_signal"
    if "manual quality" in text or "manual-watch" in text or "manual watch" in text:
        return "manual_review_hold"
    return "other_policy"


def _reason_percentages(counter: dict[str, int], total: int) -> dict[str, float]:
    if total <= 0:
        return {reason: 0.0 for reason in INGESTABILITY_REASONS}
    return {reason: round((counter.get(reason, 0) / total) * 100, 1) for reason in INGESTABILITY_REASONS}


def _top_reason(reason_counts: dict[str, int], reason_percentages: dict[str, float]) -> str:
    best_reason = INGESTABILITY_REASONS[0]
    best_score = (-1.0, -1)
    for reason in INGESTABILITY_REASONS:
        score = (reason_percentages.get(reason, 0.0), reason_counts.get(reason, 0))
        if score > best_score:
            best_reason = reason
            best_score = score
    return best_reason


def _reason_percentage_delta(candidate_add: dict[str, float], candidate_reject: dict[str, float]) -> dict[str, float]:
    return {
        reason: round(candidate_add.get(reason, 0.0) - candidate_reject.get(reason, 0.0), 1)
        for reason in INGESTABILITY_REASONS
    }


def _percentages_from_counts(counts: dict[str, int], total: int, keys: list[str]) -> dict[str, float]:
    if total <= 0:
        return {key: 0.0 for key in keys}
    return {key: round((counts.get(key, 0) / total) * 100, 1) for key in keys}


def _dominant_policy_block_type(counts: dict[str, int]) -> str:
    best_type = POLICY_BLOCK_TYPE_PRIORITY[0]
    best_score = (-1, "")
    for block_type in POLICY_BLOCK_TYPE_PRIORITY:
        score = (counts.get(block_type, 0), block_type)
        if score > best_score:
            best_type = block_type
            best_score = score
    return best_type


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


def _empty_reason_id_map() -> dict[str, list[str]]:
    return {reason: [] for reason in INGESTABILITY_REASONS}


def _normalized_reason(reason: str | None) -> str:
    return reason if reason in INGESTABILITY_REASONS else "unknown"


def _bump_reason(counter: dict[str, int], reason: str | None) -> str:
    normalized = _normalized_reason(reason)
    counter[normalized] += 1
    return normalized


def _sorted_unique(values: list[str]) -> list[str]:
    return sorted(set(values))


def _priority_ids_by_reason(reason_map: dict[str, list[str]]) -> list[str]:
    priority_ids: list[str] = []
    for reason in NON_INGESTABLE_REASON_PRIORITY:
        priority_ids.extend(_sorted_unique(reason_map.get(reason, [])))
    return priority_ids


def _promotion_queue(candidates: list[dict]) -> list[str]:
    sorted_rows = sorted(
        candidates,
        key=lambda row: (
            PROMOTION_QUEUE_PRIORITY.index(row["source_cohort"]) if row["source_cohort"] in PROMOTION_QUEUE_PRIORITY else len(PROMOTION_QUEUE_PRIORITY),
            -row.get("item_count", 0),
            row["id"],
        ),
    )
    return [row["id"] for row in sorted_rows]


def _extract_domain(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


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
            "candidate_add_non_ingestable_ids_by_reason": _empty_reason_id_map(),
            "candidate_reject_non_ingestable_ids_by_reason": _empty_reason_id_map(),
            "candidate_add_promotion_candidate_ids": [],
            "candidate_add_non_ingestable_ids": [],
            "candidate_add_non_ingestable_priority_ids": [],
            "candidate_add_failed_ids": [],
            "candidate_reject_revival_candidate_ids": [],
            "candidate_reject_non_ingestable_ids": [],
            "candidate_reject_non_ingestable_priority_ids": [],
            "candidate_reject_still_blocked_ids": [],
            "promotion_opportunity_ids": [],
            "promotion_opportunity_breakdown": {
                "candidate_add": 0,
                "candidate_reject": 0,
            },
            "promotion_opportunity_rows": [],
            "promotion_opportunity_top_rows": [],
            "promotion_opportunity_top_ids": [],
            "promotion_opportunity_cohort_percentages": {
                "candidate_add": 0.0,
                "candidate_reject": 0.0,
            },
            "promotion_opportunity_domain_counts": {},
            "promotion_opportunity_domain_percentages": {},
            "promotion_opportunity_top_domains": [],
            "promotion_opportunity_top_domain_ids": [],
            "promotion_opportunity_top_domain_share_percent": 0.0,
            "promotion_opportunity_top_domain_id_count": 0,
            "promotion_opportunity_top_domain_candidate_reject_id_count": 0,
            "promotion_opportunity_top_domain_candidate_reject_share_percent": 0.0,
            "promotion_opportunity_top_domain_candidate_reject_ids": [],
            "promotion_opportunity_top_domain_candidate_add_id_count": 0,
            "promotion_opportunity_top_domain_candidate_add_share_percent": 0.0,
            "promotion_opportunity_top_domain_candidate_add_ids": [],
            "promotion_opportunity_top_domain_cohort_mix_level": "none",
            "promotion_opportunity_domain_concentration_level": "none",
            "promotion_opportunity_candidate_reject_policy_blocked_ids": [],
            "promotion_opportunity_candidate_reject_policy_blocked_count": 0,
            "promotion_opportunity_candidate_reject_policy_blocked_share_percent": 0.0,
            "promotion_opportunity_candidate_reject_policy_blocked_ids_by_type": {
                block_type: [] for block_type in POLICY_BLOCK_TYPE_PRIORITY
            },
            "promotion_opportunity_candidate_reject_policy_blocked_counts_by_type": {
                block_type: 0 for block_type in POLICY_BLOCK_TYPE_PRIORITY
            },
            "promotion_opportunity_candidate_reject_policy_blocked_percentages_by_type": {
                block_type: 0.0 for block_type in POLICY_BLOCK_TYPE_PRIORITY
            },
            "promotion_opportunity_candidate_reject_policy_blocked_top_type": "none",
            "promotion_opportunity_candidate_reject_policy_blocked_top_type_share_percent": 0.0,
            "promotion_opportunity_candidate_reject_policy_blocked_top_type_ids": [],
            "promotion_opportunity_top_domain_policy_blocked_ids": [],
            "promotion_opportunity_top_domain_policy_blocked_count": 0,
            "promotion_opportunity_top_domain_policy_blocked_share_percent": 0.0,
        },
    }
    promotion_candidates: list[dict] = []

    for item in candidates.get("add", []):
        status = fetch_feed_status(item["url"])
        row = {"id": item["id"], "name": item.get("name", item["id"]), "url": item["url"], **status}
        results["candidate_add"].append(row)
        normalized_reason = _bump_reason(
            results["summary"]["candidate_add_reason_counts"], status.get("ingestability_reason")
        )
        if status["ok"]:
            results["summary"]["candidate_add_ok"] += 1
            if status["machine_ingestable"]:
                results["summary"]["candidate_add_promotion_candidate_ids"].append(item["id"])
                promotion_candidates.append(
                    {
                        "id": item["id"],
                        "name": item.get("name", item["id"]),
                        "url": item["url"],
                        "source_cohort": "candidate_add",
                        "item_count": status.get("item_count", 0),
                        "ingestability_reason": status.get("ingestability_reason", "machine_ingestable"),
                        "domain": _extract_domain(item["url"]),
                    }
                )
            else:
                results["summary"]["candidate_add_non_ingestable"] += 1
                results["summary"]["candidate_add_non_ingestable_ids"].append(item["id"])
                results["summary"]["candidate_add_non_ingestable_ids_by_reason"][normalized_reason].append(item["id"])
                if normalized_reason == "no_items":
                    results["summary"]["candidate_add_non_ingestable_no_items"] += 1
                elif normalized_reason == "unsupported_root_tag":
                    results["summary"]["candidate_add_non_ingestable_unsupported_root"] += 1
        else:
            results["summary"]["candidate_add_failed"] += 1
            results["summary"]["candidate_add_failed_ids"].append(item["id"])

    for item in candidates.get("reject", []):
        status = fetch_feed_status(item["url"])
        row = {"id": item["id"], "url": item["url"], "expected_reject_reason": item.get("reason", ""), **status}
        results["candidate_reject"].append(row)
        normalized_reason = _bump_reason(
            results["summary"]["candidate_reject_reason_counts"], status.get("ingestability_reason")
        )
        if status["ok"]:
            results["summary"]["candidate_reject_now_ok"] += 1
            if status["machine_ingestable"]:
                results["summary"]["candidate_reject_now_ingestable"] += 1
                results["summary"]["candidate_reject_revival_candidate_ids"].append(item["id"])
                promotion_candidates.append(
                    {
                        "id": item["id"],
                        "name": item.get("name", item["id"]),
                        "url": item["url"],
                        "source_cohort": "candidate_reject",
                        "item_count": status.get("item_count", 0),
                        "ingestability_reason": status.get("ingestability_reason", "machine_ingestable"),
                        "domain": _extract_domain(item["url"]),
                        "policy_reject_reason": item.get("reason", ""),
                        "policy_block_type": _policy_block_type(item.get("reason", "")),
                    }
                )
            else:
                results["summary"]["candidate_reject_now_non_ingestable"] += 1
                results["summary"]["candidate_reject_non_ingestable_ids"].append(item["id"])
                results["summary"]["candidate_reject_non_ingestable_ids_by_reason"][normalized_reason].append(item["id"])
        else:
            results["summary"]["candidate_reject_still_blocked"] += 1
            results["summary"]["candidate_reject_still_blocked_ids"].append(item["id"])

    results["summary"]["candidate_add_reason_percentages"] = _reason_percentages(
        results["summary"]["candidate_add_reason_counts"],
        len(results["candidate_add"]),
    )
    results["summary"]["candidate_reject_reason_percentages"] = _reason_percentages(
        results["summary"]["candidate_reject_reason_counts"],
        len(results["candidate_reject"]),
    )
    results["summary"]["candidate_add_top_ingestability_reason"] = _top_reason(
        results["summary"]["candidate_add_reason_counts"],
        results["summary"]["candidate_add_reason_percentages"],
    )
    results["summary"]["candidate_reject_top_ingestability_reason"] = _top_reason(
        results["summary"]["candidate_reject_reason_counts"],
        results["summary"]["candidate_reject_reason_percentages"],
    )
    results["summary"]["candidate_add_vs_reject_reason_percentage_delta"] = _reason_percentage_delta(
        results["summary"]["candidate_add_reason_percentages"],
        results["summary"]["candidate_reject_reason_percentages"],
    )

    id_list_keys = [
        "candidate_add_promotion_candidate_ids",
        "candidate_add_non_ingestable_ids",
        "candidate_add_failed_ids",
        "candidate_reject_revival_candidate_ids",
        "candidate_reject_non_ingestable_ids",
        "candidate_reject_still_blocked_ids",
    ]
    for key in id_list_keys:
        results["summary"][key] = _sorted_unique(results["summary"].get(key, []))

    for key in ["candidate_add_non_ingestable_ids_by_reason", "candidate_reject_non_ingestable_ids_by_reason"]:
        reason_map = results["summary"].get(key, {})
        for reason in INGESTABILITY_REASONS:
            reason_map[reason] = _sorted_unique(reason_map.get(reason, []))

    results["summary"]["candidate_add_non_ingestable_priority_ids"] = _priority_ids_by_reason(
        results["summary"].get("candidate_add_non_ingestable_ids_by_reason", {})
    )
    results["summary"]["candidate_reject_non_ingestable_priority_ids"] = _priority_ids_by_reason(
        results["summary"].get("candidate_reject_non_ingestable_ids_by_reason", {})
    )

    ranked_promotion_candidates = sorted(
        promotion_candidates,
        key=lambda row: (
            PROMOTION_QUEUE_PRIORITY.index(row["source_cohort"]) if row["source_cohort"] in PROMOTION_QUEUE_PRIORITY else len(PROMOTION_QUEUE_PRIORITY),
            -row.get("item_count", 0),
            row["id"],
        ),
    )

    results["summary"]["promotion_opportunity_ids"] = [row["id"] for row in ranked_promotion_candidates]
    for row in ranked_promotion_candidates:
        cohort = row.get("source_cohort")
        if cohort in results["summary"]["promotion_opportunity_breakdown"]:
            results["summary"]["promotion_opportunity_breakdown"][cohort] += 1

    total_promotion = len(ranked_promotion_candidates)
    if total_promotion > 0:
        for cohort in ["candidate_add", "candidate_reject"]:
            count = results["summary"]["promotion_opportunity_breakdown"].get(cohort, 0)
            results["summary"]["promotion_opportunity_cohort_percentages"][cohort] = round((count / total_promotion) * 100, 1)

    results["summary"]["promotion_opportunity_rows"] = [
        {
            "id": row["id"],
            "name": row.get("name", row["id"]),
            "url": row.get("url", ""),
            "source_cohort": row["source_cohort"],
            "item_count": row.get("item_count", 0),
            "domain": row.get("domain", _extract_domain(row.get("url", "")) or "unknown"),
            "ingestability_reason": row.get("ingestability_reason", "machine_ingestable"),
            "policy_reject_reason": row.get("policy_reject_reason", ""),
            "policy_block_type": row.get("policy_block_type", ""),
            "priority_rank": index + 1,
        }
        for index, row in enumerate(ranked_promotion_candidates)
    ]
    results["summary"]["promotion_opportunity_top_ids"] = [row["id"] for row in ranked_promotion_candidates[:5]]
    results["summary"]["promotion_opportunity_top_rows"] = results["summary"]["promotion_opportunity_rows"][:5]

    policy_blocked_rows = [
        row
        for row in results["summary"]["promotion_opportunity_rows"]
        if row.get("source_cohort") == "candidate_reject" and row.get("policy_reject_reason")
    ]
    results["summary"]["promotion_opportunity_candidate_reject_policy_blocked_ids"] = _sorted_unique(
        [row["id"] for row in policy_blocked_rows]
    )
    results["summary"]["promotion_opportunity_candidate_reject_policy_blocked_count"] = len(policy_blocked_rows)
    reject_total = results["summary"]["promotion_opportunity_breakdown"].get("candidate_reject", 0)
    if reject_total > 0:
        results["summary"]["promotion_opportunity_candidate_reject_policy_blocked_share_percent"] = round(
            (len(policy_blocked_rows) / reject_total) * 100, 1
        )
    blocked_ids_by_type = {block_type: [] for block_type in POLICY_BLOCK_TYPE_PRIORITY}
    for row in policy_blocked_rows:
        block_type = row.get("policy_block_type") or "other_policy"
        if block_type not in blocked_ids_by_type:
            blocked_ids_by_type[block_type] = []
        blocked_ids_by_type[block_type].append(row["id"])
    for block_type in blocked_ids_by_type:
        blocked_ids_by_type[block_type] = _sorted_unique(blocked_ids_by_type[block_type])
    results["summary"]["promotion_opportunity_candidate_reject_policy_blocked_ids_by_type"] = blocked_ids_by_type
    results["summary"]["promotion_opportunity_candidate_reject_policy_blocked_counts_by_type"] = {
        block_type: len(ids) for block_type, ids in blocked_ids_by_type.items()
    }
    blocked_counts_by_type = results["summary"]["promotion_opportunity_candidate_reject_policy_blocked_counts_by_type"]
    blocked_total = len(policy_blocked_rows)
    results["summary"]["promotion_opportunity_candidate_reject_policy_blocked_percentages_by_type"] = _percentages_from_counts(
        blocked_counts_by_type,
        blocked_total,
        POLICY_BLOCK_TYPE_PRIORITY,
    )
    if blocked_total > 0:
        top_block_type = _dominant_policy_block_type(blocked_counts_by_type)
        results["summary"]["promotion_opportunity_candidate_reject_policy_blocked_top_type"] = top_block_type
        results["summary"]["promotion_opportunity_candidate_reject_policy_blocked_top_type_share_percent"] = (
            results["summary"]["promotion_opportunity_candidate_reject_policy_blocked_percentages_by_type"].get(top_block_type, 0.0)
        )
        results["summary"]["promotion_opportunity_candidate_reject_policy_blocked_top_type_ids"] = blocked_ids_by_type.get(
            top_block_type, []
        )

    domain_counts: dict[str, int] = {}
    domain_ids: dict[str, list[str]] = {}
    domain_candidate_add_ids: dict[str, list[str]] = {}
    domain_candidate_reject_ids: dict[str, list[str]] = {}
    for row in ranked_promotion_candidates:
        domain = row.get("domain") or _extract_domain(row.get("url", "")) or "unknown"
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        domain_ids.setdefault(domain, []).append(row["id"])
        if row.get("source_cohort") == "candidate_add":
            domain_candidate_add_ids.setdefault(domain, []).append(row["id"])
        elif row.get("source_cohort") == "candidate_reject":
            domain_candidate_reject_ids.setdefault(domain, []).append(row["id"])
    sorted_domains = sorted(domain_counts.items(), key=lambda pair: (-pair[1], pair[0]))
    results["summary"]["promotion_opportunity_domain_counts"] = {domain: count for domain, count in sorted_domains}
    if total_promotion > 0:
        results["summary"]["promotion_opportunity_domain_percentages"] = {
            domain: round((count / total_promotion) * 100, 1) for domain, count in sorted_domains
        }
    else:
        results["summary"]["promotion_opportunity_domain_percentages"] = {}
    results["summary"]["promotion_opportunity_top_domains"] = [
        {
            "domain": domain,
            "count": count,
            "percent": results["summary"]["promotion_opportunity_domain_percentages"].get(domain, 0.0),
            "ids": _sorted_unique(domain_ids.get(domain, [])),
            "candidate_add_ids": _sorted_unique(domain_candidate_add_ids.get(domain, [])),
            "candidate_reject_ids": _sorted_unique(domain_candidate_reject_ids.get(domain, [])),
            "candidate_add_share_percent": round((len(domain_candidate_add_ids.get(domain, [])) / count) * 100, 1) if count else 0.0,
            "candidate_reject_share_percent": round((len(domain_candidate_reject_ids.get(domain, [])) / count) * 100, 1) if count else 0.0,
            "cohort_mix_level": "candidate_reject_heavy" if (round((len(domain_candidate_reject_ids.get(domain, [])) / count) * 100, 1) if count else 0.0) >= 60.0 else ("candidate_add_heavy" if (round((len(domain_candidate_add_ids.get(domain, [])) / count) * 100, 1) if count else 0.0) >= 60.0 else "balanced"),
        }
        for domain, count in sorted_domains[:5]
    ]
    results["summary"]["promotion_opportunity_top_domain_ids"] = [
        row["domain"] for row in results["summary"]["promotion_opportunity_top_domains"]
    ]

    if results["summary"]["promotion_opportunity_top_domains"]:
        top_domain_row = results["summary"]["promotion_opportunity_top_domains"][0]
        top_share = top_domain_row.get("percent", 0.0)
        results["summary"]["promotion_opportunity_top_domain_share_percent"] = top_share
        results["summary"]["promotion_opportunity_top_domain_id_count"] = top_domain_row.get("count", 0)
        results["summary"]["promotion_opportunity_top_domain_candidate_reject_id_count"] = len(
            top_domain_row.get("candidate_reject_ids", [])
        )
        results["summary"]["promotion_opportunity_top_domain_candidate_reject_share_percent"] = top_domain_row.get(
            "candidate_reject_share_percent", 0.0
        )
        results["summary"]["promotion_opportunity_top_domain_candidate_reject_ids"] = top_domain_row.get(
            "candidate_reject_ids", []
        )
        results["summary"]["promotion_opportunity_top_domain_candidate_add_id_count"] = len(
            top_domain_row.get("candidate_add_ids", [])
        )
        results["summary"]["promotion_opportunity_top_domain_candidate_add_share_percent"] = top_domain_row.get(
            "candidate_add_share_percent", 0.0
        )
        results["summary"]["promotion_opportunity_top_domain_candidate_add_ids"] = top_domain_row.get(
            "candidate_add_ids", []
        )
        results["summary"]["promotion_opportunity_top_domain_cohort_mix_level"] = top_domain_row.get(
            "cohort_mix_level", "none"
        )
        top_domain_ids = set(top_domain_row.get("ids", []))
        top_domain_policy_blocked_ids = [
            row["id"] for row in policy_blocked_rows if row["id"] in top_domain_ids
        ]
        results["summary"]["promotion_opportunity_top_domain_policy_blocked_ids"] = _sorted_unique(
            top_domain_policy_blocked_ids
        )
        results["summary"]["promotion_opportunity_top_domain_policy_blocked_count"] = len(
            results["summary"]["promotion_opportunity_top_domain_policy_blocked_ids"]
        )
        if top_domain_row.get("count", 0) > 0:
            results["summary"]["promotion_opportunity_top_domain_policy_blocked_share_percent"] = round(
                (
                    results["summary"]["promotion_opportunity_top_domain_policy_blocked_count"]
                    / top_domain_row.get("count", 0)
                )
                * 100,
                1,
            )
        if top_share >= 60.0:
            concentration_level = "high"
        elif top_share >= 35.0:
            concentration_level = "medium"
        else:
            concentration_level = "low"
        results["summary"]["promotion_opportunity_domain_concentration_level"] = concentration_level

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
    lines.append(f"- Candidate add dominant reason: {s.get('candidate_add_top_ingestability_reason', 'n/a')}")
    lines.append(f"- Candidate reject dominant reason: {s.get('candidate_reject_top_ingestability_reason', 'n/a')}")
    lines.append("- Candidate add")
    for reason, count in s["candidate_add_reason_counts"].items():
        percent = s.get("candidate_add_reason_percentages", {}).get(reason, 0.0)
        lines.append(f"  - {reason}: {count} ({percent:.1f}%)")
    lines.append("- Candidate reject")
    for reason, count in s["candidate_reject_reason_counts"].items():
        percent = s.get("candidate_reject_reason_percentages", {}).get(reason, 0.0)
        lines.append(f"  - {reason}: {count} ({percent:.1f}%)")
    lines.append("- Candidate add minus reject percentage delta")
    for reason, delta in s.get("candidate_add_vs_reject_reason_percentage_delta", {}).items():
        lines.append(f"  - {reason}: {delta:+.1f} pp")
    lines.append("")

    lines.append("## Actionable triage queues")
    lines.append(
        f"- Candidate add promotion-ready ids ({len(s.get('candidate_add_promotion_candidate_ids', []))}): "
        + (", ".join(s.get("candidate_add_promotion_candidate_ids", [])) or "none")
    )
    lines.append(
        f"- Promotion opportunity queue ids ({len(s.get('promotion_opportunity_ids', []))}): "
        + (", ".join(s.get("promotion_opportunity_ids", [])) or "none")
    )
    breakdown = s.get("promotion_opportunity_breakdown", {})
    percentages = s.get("promotion_opportunity_cohort_percentages", {})
    lines.append(
        f"  - candidate_add: {breakdown.get('candidate_add', 0)} ({percentages.get('candidate_add', 0.0):.1f}%) | candidate_reject: {breakdown.get('candidate_reject', 0)} ({percentages.get('candidate_reject', 0.0):.1f}%)"
    )
    lines.append(
        f"- Promotion opportunity top ids ({len(s.get('promotion_opportunity_top_ids', []))}): "
        + (", ".join(s.get("promotion_opportunity_top_ids", [])) or "none")
    )
    lines.append(
        f"- Promotion opportunity top domains ({len(s.get('promotion_opportunity_top_domain_ids', []))}): "
        + (", ".join(s.get("promotion_opportunity_top_domain_ids", [])) or "none")
    )
    lines.append(
        f"  - Top-domain concentration: {s.get('promotion_opportunity_domain_concentration_level', 'none')} ({s.get('promotion_opportunity_top_domain_share_percent', 0.0):.1f}% / {s.get('promotion_opportunity_top_domain_id_count', 0)} ids)"
    )
    lines.append(
        f"  - Top-domain cohort mix: {s.get('promotion_opportunity_top_domain_cohort_mix_level', 'none')}"
    )
    lines.append(
        f"  - Top-domain candidate_add share: {s.get('promotion_opportunity_top_domain_candidate_add_share_percent', 0.0):.1f}% ({s.get('promotion_opportunity_top_domain_candidate_add_id_count', 0)} ids)"
    )
    lines.append(
        f"  - Top-domain candidate_reject share: {s.get('promotion_opportunity_top_domain_candidate_reject_share_percent', 0.0):.1f}% ({s.get('promotion_opportunity_top_domain_candidate_reject_id_count', 0)} ids)"
    )
    lines.append(
        "    - candidate_add ids: "
        + (", ".join(s.get("promotion_opportunity_top_domain_candidate_add_ids", [])) or "none")
    )
    lines.append(
        "    - candidate_reject ids: "
        + (", ".join(s.get("promotion_opportunity_top_domain_candidate_reject_ids", [])) or "none")
    )
    lines.append(
        f"  - Candidate-reject policy-blocked promotion ids ({s.get('promotion_opportunity_candidate_reject_policy_blocked_count', 0)} / {breakdown.get('candidate_reject', 0)} = {s.get('promotion_opportunity_candidate_reject_policy_blocked_share_percent', 0.0):.1f}%): "
        + (", ".join(s.get("promotion_opportunity_candidate_reject_policy_blocked_ids", [])) or "none")
    )
    lines.append(
        f"  - Top-domain policy-blocked ids ({s.get('promotion_opportunity_top_domain_policy_blocked_count', 0)} / {s.get('promotion_opportunity_top_domain_id_count', 0)} = {s.get('promotion_opportunity_top_domain_policy_blocked_share_percent', 0.0):.1f}%): "
        + (", ".join(s.get("promotion_opportunity_top_domain_policy_blocked_ids", [])) or "none")
    )
    lines.append("  - Candidate-reject policy blocked breakdown:")
    counts_by_type = s.get("promotion_opportunity_candidate_reject_policy_blocked_counts_by_type", {})
    percentages_by_type = s.get("promotion_opportunity_candidate_reject_policy_blocked_percentages_by_type", {})
    for block_type, count in counts_by_type.items():
        ids = s.get("promotion_opportunity_candidate_reject_policy_blocked_ids_by_type", {}).get(block_type, [])
        percent = percentages_by_type.get(block_type, 0.0)
        lines.append(f"    - {block_type}: {count} ({percent:.1f}% | {', '.join(ids) if ids else 'none'})")
    lines.append(
        f"  - Candidate-reject policy dominant block type: {s.get('promotion_opportunity_candidate_reject_policy_blocked_top_type', 'none')} ({s.get('promotion_opportunity_candidate_reject_policy_blocked_top_type_share_percent', 0.0):.1f}% | {', '.join(s.get('promotion_opportunity_candidate_reject_policy_blocked_top_type_ids', [])) or 'none'})"
    )
    if s.get("promotion_opportunity_top_domains"):
        lines.append("  - Promotion top-domain detail (domain/count/ids):")
        for domain_row in s.get("promotion_opportunity_top_domains", []):
            lines.append(
                f"    - {domain_row.get('domain')}: {domain_row.get('count', 0)} ({domain_row.get('percent', 0.0):.1f}%) add_share={domain_row.get('candidate_add_share_percent', 0.0):.1f}% reject_share={domain_row.get('candidate_reject_share_percent', 0.0):.1f}% mix={domain_row.get('cohort_mix_level', 'balanced')} ({', '.join(domain_row.get('ids', [])) or 'none'})"
            )
    if s.get("promotion_opportunity_rows"):
        lines.append("  - Promotion queue detail (rank/cohort/items):")
        for row in s.get("promotion_opportunity_rows", []):
            policy_suffix = ""
            if row.get("source_cohort") == "candidate_reject" and row.get("policy_reject_reason"):
                policy_suffix = (
                    f", policy_block_type={row.get('policy_block_type', 'other_policy')}, "
                    f"policy_reason={row.get('policy_reject_reason')}"
                )
            lines.append(
                f"    - #{row.get('priority_rank', '?')}: {row.get('id')} ({row.get('name', row.get('id'))}) [{row.get('source_cohort')}, items={row.get('item_count', 0)}, domain={row.get('domain', 'unknown')}, reason={row.get('ingestability_reason', 'n/a')}{policy_suffix}]"
            )
            if row.get("url"):
                lines.append(f"      - {row.get('url')}")
    lines.append(
        f"- Candidate add failed ids ({len(s.get('candidate_add_failed_ids', []))}): "
        + (", ".join(s.get("candidate_add_failed_ids", [])) or "none")
    )
    lines.append(
        f"- Candidate add non-ingestable ids ({len(s.get('candidate_add_non_ingestable_ids', []))}): "
        + (", ".join(s.get("candidate_add_non_ingestable_ids", [])) or "none")
    )
    lines.append(
        f"- Candidate add non-ingestable priority ids ({len(s.get('candidate_add_non_ingestable_priority_ids', []))}): "
        + (", ".join(s.get("candidate_add_non_ingestable_priority_ids", [])) or "none")
    )
    for reason, ids in s.get("candidate_add_non_ingestable_ids_by_reason", {}).items():
        lines.append(f"  - {reason}: " + (", ".join(ids) if ids else "none"))
    lines.append(
        f"- Candidate reject revival-candidate ids ({len(s.get('candidate_reject_revival_candidate_ids', []))}): "
        + (", ".join(s.get("candidate_reject_revival_candidate_ids", [])) or "none")
    )
    lines.append(
        f"- Candidate reject still-blocked ids ({len(s.get('candidate_reject_still_blocked_ids', []))}): "
        + (", ".join(s.get("candidate_reject_still_blocked_ids", [])) or "none")
    )
    lines.append(
        f"- Candidate reject healthy-but-non-ingestable ids ({len(s.get('candidate_reject_non_ingestable_ids', []))}): "
        + (", ".join(s.get("candidate_reject_non_ingestable_ids", [])) or "none")
    )
    lines.append(
        f"- Candidate reject non-ingestable priority ids ({len(s.get('candidate_reject_non_ingestable_priority_ids', []))}): "
        + (", ".join(s.get("candidate_reject_non_ingestable_priority_ids", [])) or "none")
    )
    for reason, ids in s.get("candidate_reject_non_ingestable_ids_by_reason", {}).items():
        lines.append(f"  - {reason}: " + (", ".join(ids) if ids else "none"))
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
