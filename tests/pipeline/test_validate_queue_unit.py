import copy
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "pipeline"))

import validate_queue  # noqa: E402


def _valid_item(index=1, canonical_url=None):
    canonical_url = canonical_url or f"https://example.com/post-{index}"
    return {
        "id": f"item-{index}",
        "title": f"Item {index}",
        "canonical_url": canonical_url,
        "publisher": "Example Publisher",
        "published_at_utc": "2026-03-01T08:00:00Z",
        "source_mix_bucket": "official" if index % 2 == 0 else "independent",
        "signal": "Concrete signal line",
        "mini_abstract": "This is a concise mini abstract with source-specific context.",
        "why_click": "Open this for concrete implementation detail.",
        "confidence_label": "official" if index % 2 == 0 else "reputable community",
        "selection_reason": "in_window_ranked_selection",
        "score_total": 0.75,
        "score_relevance": 0.7,
        "score_quality": 0.8,
        "score_freshness": 0.7,
        "domain": "example.com",
        "evidence": ["Source title: Example item title with technical specifics."],
    }


def _valid_queue(items):
    return {
        "contract_version": "v2",
        "issue_id": "2026-10",
        "generated_at": "2026-03-07T10:00:00Z",
        "window_start_utc": "2026-03-02T00:00:00Z",
        "window_end_utc": "2026-03-09T00:00:00Z",
        "items": items,
        "excluded": [],
        "mix_target": {"official": 0.4, "independent": 0.6},
        "mix_actual": {"official": 0.5, "independent": 0.5},
        "quality_summary": {"domain_cap": 2},
        "composition": {
            "target_min_items": 1,
            "target_max_items": 10,
            "selected_count": len(items),
            "override": None,
        },
    }


class ValidateQueueUnitTests(unittest.TestCase):
    def test_valid_queue_passes(self):
        queue = _valid_queue([_valid_item(1), _valid_item(2, canonical_url="https://example.net/post-2")])
        validate_queue.validate_top_level(queue)
        for idx, item in enumerate(queue["items"], start=1):
            validate_queue.validate_item(idx, item)
        validate_queue.validate_domain_and_duplicates(queue["items"], queue)

    def test_rejects_duplicate_canonical_url(self):
        item1 = _valid_item(1, canonical_url="https://dup.example.com/post")
        item2 = _valid_item(2, canonical_url="https://dup.example.com/post")
        queue = _valid_queue([item1, item2])
        queue["composition"]["selected_count"] = 2
        with self.assertRaises(validate_queue.ValidationError):
            validate_queue.validate_domain_and_duplicates(queue["items"], queue)

    def test_rejects_banned_filler(self):
        item = _valid_item(1)
        item["mini_abstract"] = "It still adds practical context for your team."
        with self.assertRaises(validate_queue.ValidationError):
            validate_queue.validate_item(1, item)

    def test_rejects_why_click_with_multiple_sentences(self):
        item = _valid_item(1)
        item["why_click"] = "First sentence. Second sentence."
        with self.assertRaises(validate_queue.ValidationError):
            validate_queue.validate_item(1, item)

    def test_rejects_selected_count_out_of_range_without_override(self):
        queue = _valid_queue([_valid_item(1)])
        queue["composition"]["target_min_items"] = 8
        queue["composition"]["target_max_items"] = 10
        with self.assertRaises(validate_queue.ValidationError):
            validate_queue.validate_top_level(queue)

    def test_allows_out_of_range_when_override_enabled(self):
        queue = _valid_queue([_valid_item(1)])
        queue["composition"]["target_min_items"] = 8
        queue["composition"]["target_max_items"] = 10
        queue["composition"]["override"] = {"enabled": True, "reason": "fixture override"}
        validate_queue.validate_top_level(queue)

    def test_rejects_invalid_confidence_label(self):
        item = _valid_item(1)
        item["confidence_label"] = "unknown-level"
        with self.assertRaises(validate_queue.ValidationError):
            validate_queue.validate_item(1, item)

    def test_requires_curation_manifest_in_last_run_output_artifacts(self):
        # Mirror the WS5 contract change enforced by validate_last_run_summary.
        queue = _valid_queue([_valid_item(1)])
        validate_queue.validate_top_level(queue)

        broken = copy.deepcopy(queue)
        del broken["quality_summary"]
        with self.assertRaises(validate_queue.ValidationError):
            validate_queue.validate_top_level(broken)


if __name__ == "__main__":
    unittest.main()
