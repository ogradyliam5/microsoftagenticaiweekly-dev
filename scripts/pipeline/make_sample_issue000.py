#!/usr/bin/env python3
import datetime as dt
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

issue_id = "000"
now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

sample_items = [
    {
        "id": "sample-official-copilot-studio",
        "title": "Sample: Copilot Studio capability update",
        "url": "https://example.com/official-copilot-update",
        "canonical_url": "https://example.com/official-copilot-update",
        "author": "",
        "publisher": "Microsoft (sample)",
        "published_at": now,
        "published_at_utc": now,
        "fetched_at": now,
        "product_area": "Power Platform",
        "source_type": "rss",
        "source_mix_bucket": "official",
        "content_type": "update",
        "score_freshness": 1.0,
        "score_quality": 0.95,
        "score_relevance": 0.9,
        "score_total": 0.95,
        "domain": "example.com",
        "signal": "Copilot Studio capability update",
        "mini_abstract": "Sample v2 item from an official source. Included for pipeline contract verification.",
        "why_click": "Open this for primary-source release detail.",
        "confidence_label": "official",
        "selection_reason": "sample_fixture",
        "tags": ["Power Platform", "Official"],
        "evidence": ["Source title: Sample Copilot Studio capability update"],
        "summary_bullets": ["Sample v2 item from an official source."],
        "why_it_matters": "Open this for primary-source release detail.",
        "confidence": "High",
    },
    {
        "id": "sample-community-foundry",
        "title": "Sample: Foundry agent ops pattern",
        "url": "https://example.org/foundry-pattern",
        "canonical_url": "https://example.org/foundry-pattern",
        "author": "",
        "publisher": "Community (sample)",
        "published_at": now,
        "published_at_utc": now,
        "fetched_at": now,
        "product_area": "Foundry",
        "source_type": "rss",
        "source_mix_bucket": "independent",
        "content_type": "guide",
        "score_freshness": 0.9,
        "score_quality": 0.8,
        "score_relevance": 0.8,
        "score_total": 0.83,
        "domain": "example.org",
        "signal": "Foundry agent operations pattern",
        "mini_abstract": "Sample v2 item from a community source. Included to test story-unit rendering.",
        "why_click": "Open this for concise implementation notes.",
        "confidence_label": "reputable community",
        "selection_reason": "sample_fixture",
        "tags": ["Foundry", "Community"],
        "evidence": ["Source title: Sample Foundry agent operations pattern"],
        "summary_bullets": ["Sample v2 item from a community source."],
        "why_it_matters": "Open this for concise implementation notes.",
        "confidence": "Medium",
    },
]

queue = {
    "contract_version": "v2",
    "issue_id": issue_id,
    "generated_at": now,
    "window_start_utc": now,
    "window_end_utc": now,
    "fallback_start_utc": now,
    "items": sample_items,
    "excluded": [],
    "mix_target": {"independent": 0.6, "official": 0.4},
    "mix_actual": {
        "official": 0.5,
        "independent": 0.5,
        "official_count": 1,
        "independent_count": 1,
    },
    "selection_stats": {
        "in_window_count": 2,
        "fallback_pool_count": 0,
        "fallback_used_count": 0,
        "target_min_items": 8,
        "target_max_items": 10,
    },
    "composition": {
        "target_min_items": 8,
        "target_max_items": 10,
        "selected_count": 2,
        "override": {
            "enabled": True,
            "reason": "Sample fixture intentionally below production issue size.",
        },
    },
    "quality_summary": {
        "domain_cap": 2,
        "duplicate_rejections": 0,
        "blandness_rejections": 0,
        "low_relevance_rejections": 0,
        "selection_count": 2,
        "selected_unique_domains": 2,
        "top_domain_share_percent": 50.0,
    },
    "questions_for_liam": ["Sample run only."],
}

manifest = {
    "contract_version": "v2",
    "issue_id": issue_id,
    "generated_at": now,
    "selected_item_ids": [item["id"] for item in sample_items],
    "excluded_items": [],
    "reason_counts": {},
    "domain_diversity": {
        "domain_cap": 2,
        "selected_domain_counts": {"example.com": 1, "example.org": 1},
        "selected_unique_domains": 2,
        "cap_exceeded": False,
    },
    "source_bucket_mix": {
        "official_count": 1,
        "independent_count": 1,
        "official_pct": 0.5,
        "independent_pct": 0.5,
    },
    "quality_gate_results": {
        "relevance_threshold": 0.55,
        "domain_cap": 2,
        "target_min_items": 8,
        "target_max_items": 10,
        "composition_override": queue["composition"]["override"],
        "counts": queue["quality_summary"],
    },
}

(ART / f"editorial_queue-{issue_id}.json").write_text(json.dumps(queue, indent=2), encoding="utf-8")
(ART / f"editorial_queue-{issue_id}.md").write_text(
    "# Weekly Editorial Queue - 000\n\nSample v2 queue artifact for verification.\n",
    encoding="utf-8",
)
(ART / f"curation_manifest-{issue_id}.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

posts = ROOT / "posts"
drafts = ROOT / "drafts"
posts.mkdir(exist_ok=True)
drafts.mkdir(exist_ok=True)

(posts / "issue-000.md").write_text(
    "# Microsoft Agentic AI Weekly - Week of sample\n\nSample issue generated for v2 pipeline verification.\n",
    encoding="utf-8",
)
(drafts / "email-000.md").write_text(
    "# Microsoft Agentic AI Weekly - Week of sample\n\nSample email draft. Approval required.\n",
    encoding="utf-8",
)

print("Generated sample Issue 000 v2 artifacts")
