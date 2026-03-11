#!/usr/bin/env python3
import argparse
import datetime as dt
import email.utils
import json
import pathlib
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"

CONTRACT_VERSION = "v2"
TARGET_MIN_ITEMS = 8
TARGET_MAX_ITEMS = 10
DEFAULT_MIX_TARGET = {"independent": 0.60, "official": 0.40}
RELEVANCE_MIN_SCORE = 0.55
MAX_FEED_ITEMS = 40
FALLBACK_LOOKBACK_DAYS = 21
DOMAIN_CAP_PER_ISSUE = 2

CONTENT_TYPE_WEIGHTS = {
    "update": 1.0,
    "guide": 0.95,
    "howto": 0.92,
    "demo": 0.88,
    "build_report": 0.85,
    "release_notes": 0.82,
    "analysis": 0.72,
    "news": 0.58,
    "marketing": 0.35,
    "other": 0.55,
}

BANNED_FILLER_PATTERNS = [
    "it still adds practical context",
    "use it to tighten",
    "use it to inform next-sprint priorities",
    "useful if this area is in your current delivery scope",
    "potentially relevant update",
]


def text(value):
    return (value or "").strip()


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:80]


def normalize_url(value):
    if not value:
        return ""
    parsed = urllib.parse.urlsplit(value.strip())
    query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=False)
    filtered_query = [
        (key, val)
        for key, val in query_pairs
        if not key.lower().startswith("utm_") and key.lower() not in {"fbclid", "gclid"}
    ]
    normalized = urllib.parse.urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path,
            urllib.parse.urlencode(filtered_query),
            "",
        )
    )
    return normalized


def domain_from_url(value):
    try:
        host = urllib.parse.urlsplit(value).netloc.lower()
        if host.startswith("www."):
            return host[4:]
        return host
    except Exception:
        return "unknown"


def parse_date(value):
    if not value:
        return None
    try:
        return email.utils.parsedate_to_datetime(value)
    except Exception:
        pass
    try:
        normalized = value.replace("Z", "+00:00")
        return dt.datetime.fromisoformat(normalized)
    except Exception:
        return None


def weekly_window(now):
    week_start = (now - dt.timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    previous_week_start = week_start - dt.timedelta(days=7)
    return previous_week_start, week_start


def fetch_rss(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read()


def parse_feed(raw):
    out = []
    root = ET.fromstring(raw)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    if root.tag.endswith("feed"):
        entries = root.findall("atom:entry", ns)
        for entry in entries[:MAX_FEED_ITEMS]:
            title = text(entry.findtext("atom:title", default="", namespaces=ns))
            link_el = entry.find("atom:link", ns)
            link = link_el.attrib.get("href", "") if link_el is not None else ""
            pub = text(entry.findtext("atom:updated", default="", namespaces=ns))
            out.append((title, link, pub))
    else:
        for item in root.findall("./channel/item")[:MAX_FEED_ITEMS]:
            title = text(item.findtext("title", default=""))
            link = text(item.findtext("link", default=""))
            pub = text(item.findtext("pubDate", default=""))
            out.append((title, link, pub))

    return out


def classify_area(title, source_area):
    t = title.lower()
    tags = []
    if source_area == "Power Platform" or any(k in t for k in ["copilot studio", "power automate", "power apps", "dataverse"]):
        tags.append("Power Platform")
    if source_area == "M365" or any(k in t for k in ["microsoft 365", "teams", "graph", "sharepoint", "office add-in"]):
        tags.append("M365")
    if source_area == "Foundry" or any(k in t for k in ["azure ai", "foundry", "agent", "model", "semantic kernel"]):
        tags.append("Foundry")
    return tags or [source_area or "Mixed"]


def classify_content_type(title):
    t = title.lower()

    if any(k in t for k in ["release notes", "changelog", "what's new", "whats new", "general availability", "public preview", "ga"]):
        return "update"
    if any(k in t for k in ["how to", "how-to", "walkthrough", "step-by-step", "tutorial"]):
        return "howto"
    if any(k in t for k in ["guide", "playbook", "best practices", "reference architecture"]):
        return "guide"
    if any(k in t for k in ["demo", "sample", "example", "showcase"]):
        return "demo"
    if any(k in t for k in ["we built", "case study", "in production", "lessons learned"]):
        return "build_report"
    if any(k in t for k in ["release wave", "monthly update", "patch notes"]):
        return "release_notes"
    if any(k in t for k in ["analysis", "deep dive", "benchmark", "comparison"]):
        return "analysis"
    if any(k in t for k in ["announcing", "launch", "news", "recap"]):
        return "news"
    if any(k in t for k in ["webinar", "event", "register", "sponsored", "keynote"]):
        return "marketing"
    return "other"


def recency_score(published_at, now):
    parsed = parse_date(published_at)
    if not parsed:
        return 0.30
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    age_days = (now - parsed.astimezone(dt.timezone.utc)).total_seconds() / 86400
    if age_days <= 3:
        return 1.0
    if age_days <= 7:
        return 0.85
    if age_days <= 14:
        return 0.60
    if age_days <= 30:
        return 0.35
    return 0.15


def quality_score(source, title):
    title_l = title.lower()
    source_priority = min(max(source.get("priority", 5), 1), 10) / 10
    trust = 1.0 if source.get("trust") == "official" else 0.85
    title_penalty = 0.10 if any(k in title_l for k in ["roundup", "link list", "week in review"]) else 0.0

    content_type = classify_content_type(title)
    content_type_weight = CONTENT_TYPE_WEIGHTS.get(content_type, CONTENT_TYPE_WEIGHTS["other"])
    content_adjustment = (content_type_weight - 0.50) * 0.30

    quality = (source_priority * 0.55) + (trust * 0.30) + (content_type_weight * 0.15) + content_adjustment - title_penalty
    return max(0.0, min(1.0, quality)), content_type, round(content_type_weight, 4)


def relevance_score(title, source_area, content_type):
    t = (title or "").lower()
    area = (source_area or "").lower()

    ai_core = [
        "agent", "agentic", "copilot", "copilot studio", "foundry", "azure ai",
        "semantic kernel", "autogen", "mcp", "llm", "prompt", "rag", "grounding"
    ]
    ai_ops = [
        "governance", "guardrail", "policy", "eval", "evaluation", "orchestration", "automation", "genai"
    ]
    microsoft_context = [
        "power platform", "power apps", "power automate", "dataverse", "m365", "microsoft 365", "teams", "graph", "azure"
    ]
    off_topic = [
        "xbox", "surface", "gaming", "holiday", "career", "job", "merch", "investor", "leadership change"
    ]

    has_ai_core = any(k in t for k in ai_core)
    has_ai_ops = any(k in t for k in ai_ops)
    has_context = any(k in t for k in microsoft_context) or any(k in area for k in ["power platform", "m365", "foundry", "mixed"])

    if not (has_ai_core or has_ai_ops):
        return 0.0

    score = 0.0
    score += 0.60 if has_ai_core else 0.0
    score += 0.20 if has_ai_ops else 0.0
    score += 0.15 if has_context else 0.0

    if content_type in {"marketing", "news"}:
        score -= 0.20
    if any(k in t for k in off_topic):
        score -= 0.55

    return max(0.0, min(1.0, round(score, 4)))


def total_score(freshness, quality, relevance):
    return round((freshness * 0.35) + (quality * 0.35) + (relevance * 0.30), 4)


def infer_focus(title, product_area):
    title_l = title.lower()
    if "copilot studio" in title_l:
        return "Copilot Studio implementation"
    if "foundry" in title_l or "semantic kernel" in title_l:
        return "Foundry and agent framework delivery"
    if "m365" in title_l or "microsoft 365" in title_l or "sharepoint" in title_l:
        return "Microsoft 365 extensibility and operations"
    if "power automate" in title_l or "power apps" in title_l or "dataverse" in title_l:
        return "Power Platform build and automation design"
    if "governance" in title_l or "security" in title_l or "rbac" in title_l:
        return "governance and control design"
    if product_area == "Foundry":
        return "Azure AI and Foundry execution choices"
    if product_area == "M365":
        return "M365 platform and workflow impact"
    if product_area == "Power Platform":
        return "Power Platform implementation details"
    return "Microsoft agent delivery decisions"


def sentence_cap(value, max_chars):
    value = re.sub(r"\s+", " ", (value or "").strip())
    if len(value) <= max_chars:
        return value
    clipped = value[:max_chars].rsplit(" ", 1)[0].strip()
    return clipped + "..."


def synthesize_signal(item):
    title = re.sub(r"\s+", " ", item.get("title", "").strip())
    return sentence_cap(title, 130)


def synthesize_mini_abstract(item):
    content_type = item.get("content_type", "other")
    product_area = item.get("product_area", "Mixed")
    trust = item.get("trust", "community")
    focus = infer_focus(item.get("title", ""), product_area)

    type_phrase = {
        "update": "a platform update",
        "guide": "a practical guide",
        "howto": "a step-by-step walkthrough",
        "demo": "a concrete demo",
        "build_report": "a field implementation report",
        "release_notes": "a release-level change summary",
        "analysis": "an analysis of trade-offs",
        "news": "an announcement with delivery implications",
        "marketing": "an announcement that needs filtering",
        "other": "a focused technical post",
    }.get(content_type, "a technical update")

    source_line = "from a primary Microsoft source" if trust == "official" else "from a practitioner source"
    sentence_one = f"This is {type_phrase} on {focus} {source_line}."

    if content_type in {"guide", "howto", "demo", "build_report"}:
        sentence_two = "It includes concrete implementation detail rather than high-level commentary."
    elif content_type in {"update", "release_notes"}:
        sentence_two = "It helps teams track changes that can affect architecture and rollout decisions."
    elif content_type == "analysis":
        sentence_two = "It highlights trade-offs that are useful before adopting a pattern or tool."
    else:
        sentence_two = "It adds source-grounded context that is relevant to near-term delivery planning."

    combined = f"{sentence_one} {sentence_two}"
    return sentence_cap(combined, 260)


def synthesize_why_click(item):
    content_type = item.get("content_type", "other")
    trust = item.get("trust", "community")

    if trust == "official":
        base = "Open this for primary-source detail on Microsoft platform direction and release specifics."
    elif content_type in {"guide", "howto", "demo", "build_report"}:
        base = "Open this for implementation detail you can compare directly against your current approach."
    elif content_type == "analysis":
        base = "Open this for concise trade-off framing before deciding whether to adopt the pattern."
    else:
        base = "Open this for concise context and concrete specifics beyond headline-level summaries."

    return sentence_cap(base, 170)


def confidence_label(item):
    if item.get("trust") == "official":
        return "official"

    quality = item.get("score_quality", 0)
    relevance = item.get("score_relevance", 0)
    if quality >= 0.72 and relevance >= 0.6:
        return "reputable community"
    return "early signal"


def is_bland(text_value):
    value = (text_value or "").lower()
    if not value:
        return True
    for phrase in BANNED_FILLER_PATTERNS:
        if phrase in value:
            return True
    # catch repetitive low-information templates
    if re.search(r"\b(use it to|practical context|current delivery scope)\b", value):
        return True
    return False


def add_excluded(excluded, reason_code, reason_detail, item=None, source=None, extra=None):
    row = {
        "reason_code": reason_code,
        "reason_detail": reason_detail,
    }
    if item:
        row.update({
            "id": item.get("id"),
            "title": item.get("title"),
            "canonical_url": item.get("canonical_url"),
            "domain": item.get("domain"),
        })
    if source:
        row["source"] = source
    if extra:
        row.update(extra)
    excluded.append(row)


def pick_from_pool(pool, need, selected, domain_counts, domain_cap, reason_code_if_skipped):
    skipped = []
    while need > 0 and pool:
        candidate = pool.pop(0)
        candidate_domain = candidate.get("domain", "unknown")
        if domain_counts[candidate_domain] >= domain_cap:
            skipped.append((candidate, reason_code_if_skipped))
            continue

        selected.append(candidate)
        domain_counts[candidate_domain] += 1
        need -= 1

    return need, skipped


def select_items(candidates, fallback_candidates, mix_target, excluded):
    ranked = sorted(candidates, key=lambda x: x["score_total"], reverse=True)
    ranked_fallback = sorted(fallback_candidates, key=lambda x: x["score_total"], reverse=True)

    official_target = round(TARGET_MAX_ITEMS * mix_target.get("official", DEFAULT_MIX_TARGET["official"]))
    independent_target = TARGET_MAX_ITEMS - official_target

    official_pool = [item for item in ranked if item["source_mix_bucket"] == "official"]
    independent_pool = [item for item in ranked if item["source_mix_bucket"] == "independent"]

    selected = []
    domain_counts = Counter()

    remaining, skipped_independent = pick_from_pool(
        independent_pool,
        independent_target,
        selected,
        domain_counts,
        DOMAIN_CAP_PER_ISSUE,
        "domain_cap_exceeded",
    )

    remaining_official_need = official_target
    remaining_official_need, skipped_official = pick_from_pool(
        official_pool,
        remaining_official_need,
        selected,
        domain_counts,
        DOMAIN_CAP_PER_ISSUE,
        "domain_cap_exceeded",
    )

    leftovers = [item for item in ranked if item not in selected]
    remaining_total = TARGET_MAX_ITEMS - len(selected)
    remaining_total, skipped_fill = pick_from_pool(
        leftovers,
        remaining_total,
        selected,
        domain_counts,
        DOMAIN_CAP_PER_ISSUE,
        "domain_cap_exceeded",
    )

    fallback_used = 0
    if len(selected) < TARGET_MIN_ITEMS and ranked_fallback:
        fallback_leftovers = [item for item in ranked_fallback if item not in selected]
        need = TARGET_MIN_ITEMS - len(selected)
        before = len(selected)
        need, skipped_fallback = pick_from_pool(
            fallback_leftovers,
            need,
            selected,
            domain_counts,
            DOMAIN_CAP_PER_ISSUE,
            "domain_cap_exceeded",
        )
        fallback_used = len(selected) - before
        skipped_fill.extend(skipped_fallback)

    for candidate, reason_code in skipped_independent + skipped_official + skipped_fill:
        add_excluded(
            excluded,
            reason_code,
            "Domain concentration cap reached for selected issue set.",
            item=candidate,
        )

    selected = sorted(selected, key=lambda x: x["score_total"], reverse=True)

    for index, item in enumerate(selected, start=1):
        if item.get("fallback_reason"):
            item["selection_reason"] = "fallback_recent_pre_window"
        else:
            item["selection_reason"] = "in_window_ranked_selection"
        item["selection_rank"] = index

    composition_override = None
    if len(selected) < TARGET_MIN_ITEMS:
        composition_override = {
            "enabled": True,
            "reason": "Insufficient quality candidates within relevance, blandness, and domain-cap constraints.",
        }

    return selected[:TARGET_MAX_ITEMS], fallback_used, composition_override


def build_queue(issue_id):
    source_doc = json.loads((ROOT / "data/sources.json").read_text(encoding="utf-8"))
    sources = source_doc["sources"]
    mix_target = source_doc.get("mix_target", DEFAULT_MIX_TARGET)

    now = dt.datetime.now(dt.timezone.utc)
    window_start, window_end = weekly_window(now)
    fallback_start = window_start - dt.timedelta(days=FALLBACK_LOOKBACK_DAYS)

    items_in_window = []
    fallback_items = []
    excluded = []

    seen_title_keys = set()
    seen_url_keys = set()

    quality_counts = Counter()

    for source in sources:
        if source.get("type") not in {"rss", "github"}:
            add_excluded(
                excluded,
                "unsupported_source_type",
                "Source type is not machine-ingestable for automated queue build.",
                source=source.get("id"),
            )
            continue

        try:
            raw = fetch_rss(source["url"])
            entries = parse_feed(raw)
        except Exception as exc:
            add_excluded(
                excluded,
                "fetch_error",
                f"Failed to fetch source feed: {exc}",
                source=source.get("id"),
            )
            continue

        for title, url, published_at in entries:
            if not title or not url:
                add_excluded(
                    excluded,
                    "missing_required_fields",
                    "Feed item missing title or URL.",
                    source=source.get("id"),
                    extra={"title": title, "url": url},
                )
                continue

            canonical_url = normalize_url(url)
            title_key = slug(title)
            url_key = canonical_url.lower()

            if title_key in seen_title_keys or url_key in seen_url_keys:
                quality_counts["duplicate_rejections"] += 1
                add_excluded(
                    excluded,
                    "duplicate",
                    "Duplicate title or canonical URL in current queue build.",
                    source=source.get("id"),
                    extra={"title": title, "canonical_url": canonical_url},
                )
                continue

            parsed_pub = parse_date(published_at)
            if not parsed_pub:
                add_excluded(
                    excluded,
                    "missing_required_fields",
                    "Missing or invalid published_at value.",
                    source=source.get("id"),
                    extra={"title": title, "canonical_url": canonical_url},
                )
                continue

            if parsed_pub.tzinfo is None:
                parsed_pub = parsed_pub.replace(tzinfo=dt.timezone.utc)
            published_at_utc = parsed_pub.astimezone(dt.timezone.utc)

            quality, content_type, content_type_weight = quality_score(source, title)
            freshness = recency_score(published_at, now)
            relevance = relevance_score(title, source.get("product_area", "Mixed"), content_type)
            if relevance < RELEVANCE_MIN_SCORE:
                quality_counts["low_relevance_rejections"] += 1
                add_excluded(
                    excluded,
                    "low_relevance",
                    "Item score below relevance threshold.",
                    source=source.get("id"),
                    extra={
                        "title": title,
                        "canonical_url": canonical_url,
                        "score_relevance": relevance,
                    },
                )
                continue

            score_total = total_score(freshness, quality, relevance)
            tags = classify_area(title, source.get("product_area", "Mixed"))
            source_mix_bucket = "official" if source.get("trust") == "official" else "independent"
            domain = domain_from_url(canonical_url)

            base_item = {
                "id": slug(f"{domain}-{title}"),
                "title": title,
                "url": canonical_url,
                "canonical_url": canonical_url,
                "author": "",
                "publisher": source.get("name", "Unknown source"),
                "published_at": published_at,
                "published_at_utc": published_at_utc.isoformat(),
                "fetched_at": now.isoformat(),
                "product_area": source.get("product_area", "Mixed"),
                "source_type": source.get("type", "rss"),
                "source_mix_bucket": source_mix_bucket,
                "content_type": content_type,
                "score_freshness": round(freshness, 4),
                "score_quality": round(quality, 4),
                "score_content_type": content_type_weight,
                "score_relevance": relevance,
                "score_total": score_total,
                "tags": tags + (["Official"] if source_mix_bucket == "official" else ["Community"]),
                "domain": domain,
                "trust": source.get("trust", "community"),
            }

            base_item["signal"] = synthesize_signal(base_item)
            base_item["mini_abstract"] = synthesize_mini_abstract(base_item)
            base_item["why_click"] = synthesize_why_click(base_item)
            base_item["confidence_label"] = confidence_label(base_item)
            base_item["selection_reason"] = "pending_selection"
            base_item["evidence"] = [f"Source title: {sentence_cap(title, 120)}"]

            # Backward-friendly fields for legacy scripts.
            base_item["summary_bullets"] = [base_item["mini_abstract"]]
            base_item["why_it_matters"] = base_item["why_click"]
            base_item["confidence"] = {
                "official": "High",
                "reputable community": "Medium",
                "early signal": "Low",
            }.get(base_item["confidence_label"], "Medium")

            bland = is_bland(base_item["mini_abstract"]) or is_bland(base_item["why_click"])
            if bland:
                quality_counts["blandness_rejections"] += 1
                add_excluded(
                    excluded,
                    "bland_summary",
                    "Generated summary failed anti-slop blandness checks.",
                    item=base_item,
                )
                continue

            seen_title_keys.add(title_key)
            seen_url_keys.add(url_key)

            if window_start <= published_at_utc < window_end:
                items_in_window.append(base_item)
            elif fallback_start <= published_at_utc < window_start:
                base_item["fallback_reason"] = "recent_pre_window_backfill"
                fallback_items.append(base_item)
            else:
                add_excluded(
                    excluded,
                    "outside_collection_window",
                    "Item is outside the target collection window and fallback range.",
                    item=base_item,
                )

    selected_items, fallback_used_count, composition_override = select_items(
        items_in_window,
        fallback_items,
        mix_target,
        excluded,
    )

    selected_domain_counts = Counter(item.get("domain", "unknown") for item in selected_items)
    selected_bucket_counts = Counter(item.get("source_mix_bucket", "unknown") for item in selected_items)

    official_count = selected_bucket_counts.get("official", 0)
    independent_count = selected_bucket_counts.get("independent", 0)
    selected_count = len(selected_items)

    quality_summary = {
        "domain_cap": DOMAIN_CAP_PER_ISSUE,
        "duplicate_rejections": quality_counts["duplicate_rejections"],
        "blandness_rejections": quality_counts["blandness_rejections"],
        "low_relevance_rejections": quality_counts["low_relevance_rejections"],
        "selection_count": selected_count,
        "selected_unique_domains": len(selected_domain_counts),
        "top_domain_share_percent": round((max(selected_domain_counts.values()) / selected_count) * 100, 2) if selected_count else 0.0,
    }

    curation_manifest = {
        "contract_version": CONTRACT_VERSION,
        "issue_id": issue_id,
        "generated_at": now.isoformat(),
        "selected_item_ids": [item["id"] for item in selected_items],
        "excluded_items": excluded,
        "reason_counts": dict(Counter(row.get("reason_code", "unknown") for row in excluded)),
        "domain_diversity": {
            "domain_cap": DOMAIN_CAP_PER_ISSUE,
            "selected_domain_counts": dict(selected_domain_counts),
            "selected_unique_domains": len(selected_domain_counts),
            "cap_exceeded": any(count > DOMAIN_CAP_PER_ISSUE for count in selected_domain_counts.values()),
        },
        "source_bucket_mix": {
            "official_count": official_count,
            "independent_count": independent_count,
            "official_pct": round((official_count / selected_count), 3) if selected_count else 0,
            "independent_pct": round((independent_count / selected_count), 3) if selected_count else 0,
        },
        "quality_gate_results": {
            "relevance_threshold": RELEVANCE_MIN_SCORE,
            "blandness_patterns": BANNED_FILLER_PATTERNS,
            "domain_cap": DOMAIN_CAP_PER_ISSUE,
            "target_min_items": TARGET_MIN_ITEMS,
            "target_max_items": TARGET_MAX_ITEMS,
            "composition_override": composition_override,
            "counts": quality_summary,
        },
    }

    queue = {
        "contract_version": CONTRACT_VERSION,
        "issue_id": issue_id,
        "generated_at": now.isoformat(),
        "window_start_utc": window_start.isoformat(),
        "window_end_utc": window_end.isoformat(),
        "fallback_start_utc": fallback_start.isoformat(),
        "items": selected_items,
        "excluded": excluded,
        "mix_target": mix_target,
        "mix_actual": {
            "official": round((official_count / selected_count), 3) if selected_count else 0,
            "independent": round((independent_count / selected_count), 3) if selected_count else 0,
            "official_count": official_count,
            "independent_count": independent_count,
        },
        "selection_stats": {
            "in_window_count": len(items_in_window),
            "fallback_pool_count": len(fallback_items),
            "fallback_used_count": fallback_used_count,
            "target_min_items": TARGET_MIN_ITEMS,
            "target_max_items": TARGET_MAX_ITEMS,
        },
        "composition": {
            "target_min_items": TARGET_MIN_ITEMS,
            "target_max_items": TARGET_MAX_ITEMS,
            "selected_count": selected_count,
            "override": composition_override,
        },
        "quality_summary": quality_summary,
        "questions_for_liam": [
            "Any source changes needed this week? (approval required)",
            "Any selected item that should be excluded despite score?",
        ],
    }

    return queue, curation_manifest


def render_queue_markdown(queue, manifest):
    issue_id = queue["issue_id"]
    items = queue.get("items", [])
    reason_counts = manifest.get("reason_counts", {})
    quality_summary = queue.get("quality_summary", {})

    lines = [
        f"# Weekly Editorial Queue - {issue_id}",
        "",
        f"Contract version: `{queue.get('contract_version', 'unknown')}`",
        f"Generated: `{queue.get('generated_at')}`",
        f"Selected items: `{len(items)}`",
        f"Excluded items: `{len(queue.get('excluded', []))}`",
        "",
        "## Composition and quality",
        "",
        f"- Target range: {queue['composition']['target_min_items']} to {queue['composition']['target_max_items']}",
        f"- Selected count: {queue['composition']['selected_count']}",
        f"- Domain cap per issue: {quality_summary.get('domain_cap')}",
        f"- Unique selected domains: {quality_summary.get('selected_unique_domains')}",
        f"- Top domain share: {quality_summary.get('top_domain_share_percent')}%",
        f"- Duplicate rejections: {quality_summary.get('duplicate_rejections')}",
        f"- Blandness rejections: {quality_summary.get('blandness_rejections')}",
        f"- Low-relevance rejections: {quality_summary.get('low_relevance_rejections')}",
        "",
        "## Selected items",
        "",
    ]

    if not items:
        lines.append("- No qualifying items selected.")
    else:
        for idx, item in enumerate(items, start=1):
            lines.extend([
                f"{idx}. **{item.get('title')}**",
                f"   - Source: {item.get('publisher')} ({item.get('source_mix_bucket')})",
                f"   - Domain: {item.get('domain')}",
                f"   - Signal: {item.get('signal')}",
                f"   - Mini-abstract: {item.get('mini_abstract')}",
                f"   - Why click: {item.get('why_click')}",
                f"   - Confidence: {item.get('confidence_label')}",
                f"   - Selection reason: {item.get('selection_reason')}",
                f"   - Score: {item.get('score_total')} (freshness {item.get('score_freshness')}, quality {item.get('score_quality')}, relevance {item.get('score_relevance')})",
                f"   - URL: {item.get('canonical_url')}",
            ])

    lines.extend([
        "",
        "## Exclusion reason counts",
        "",
    ])

    if reason_counts:
        for reason_code, count in sorted(reason_counts.items(), key=lambda pair: pair[0]):
            lines.append(f"- {reason_code}: {count}")
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Questions for Liam",
        "",
    ])

    for q in queue.get("questions_for_liam", []):
        lines.append(f"- {q}")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-id", required=True)
    args = parser.parse_args()

    queue, manifest = build_queue(args.issue_id)

    ART.mkdir(exist_ok=True)
    queue_json_path = ART / f"editorial_queue-{args.issue_id}.json"
    queue_md_path = ART / f"editorial_queue-{args.issue_id}.md"
    manifest_json_path = ART / f"curation_manifest-{args.issue_id}.json"

    queue_json_path.write_text(json.dumps(queue, indent=2), encoding="utf-8")
    queue_md_path.write_text(render_queue_markdown(queue, manifest), encoding="utf-8")
    manifest_json_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(str(queue_json_path))
    print(str(queue_md_path))
    print(str(manifest_json_path))


if __name__ == "__main__":
    main()
