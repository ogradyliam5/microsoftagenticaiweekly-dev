import pathlib
import sys
import unittest
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "pipeline"))

import build_queue  # noqa: E402


def _candidate(index, bucket, domain, score_total):
    return {
        "id": f"{bucket}-{index}",
        "source_mix_bucket": bucket,
        "domain": domain,
        "score_total": score_total,
    }


class BuildQueueUnitTests(unittest.TestCase):
    def test_normalize_url_strips_tracking_params(self):
        raw = "HTTPS://WWW.Example.com/path?a=1&utm_source=x&fbclid=y&b=2"
        normalized = build_queue.normalize_url(raw)
        self.assertEqual(normalized, "https://www.example.com/path?a=1&b=2")

    def test_domain_from_url_strips_www(self):
        self.assertEqual(build_queue.domain_from_url("https://www.example.com/a"), "example.com")
        self.assertEqual(build_queue.domain_from_url("https://sub.example.com/a"), "sub.example.com")

    def test_sentence_cap_truncates_with_ellipsis(self):
        text = " ".join(["word"] * 60)
        capped = build_queue.sentence_cap(text, 40)
        self.assertTrue(capped.endswith("..."))
        self.assertLessEqual(len(capped), 43)

    def test_is_bland_detects_banned_pattern(self):
        bland = "Use it to inform next-sprint priorities for your program."
        self.assertTrue(build_queue.is_bland(bland))
        self.assertFalse(build_queue.is_bland("Concrete implementation details with source-backed claims."))

    def test_confidence_label(self):
        official = {"trust": "official", "score_quality": 0.1, "score_relevance": 0.1}
        reputable = {"trust": "community", "score_quality": 0.8, "score_relevance": 0.7}
        early = {"trust": "community", "score_quality": 0.6, "score_relevance": 0.55}

        self.assertEqual(build_queue.confidence_label(official), "official")
        self.assertEqual(build_queue.confidence_label(reputable), "reputable community")
        self.assertEqual(build_queue.confidence_label(early), "early signal")

    def test_select_items_applies_domain_cap_and_sets_override(self):
        candidates = []
        for i in range(6):
            candidates.append(_candidate(i, "independent", "a.example.com", 0.99 - (i * 0.01)))
            candidates.append(_candidate(i, "official", "b.example.com", 0.89 - (i * 0.01)))

        excluded = []
        selected, fallback_used_count, composition_override = build_queue.select_items(
            candidates=candidates,
            fallback_candidates=[],
            mix_target={"official": 0.4, "independent": 0.6},
            excluded=excluded,
        )

        self.assertEqual(fallback_used_count, 0)
        self.assertIsNotNone(composition_override)
        self.assertTrue(composition_override["enabled"])

        domain_counts = Counter(item["domain"] for item in selected)
        self.assertTrue(domain_counts)
        self.assertTrue(all(count <= build_queue.DOMAIN_CAP_PER_ISSUE for count in domain_counts.values()))

        # With two domains and cap=2, max selected items should be 4.
        self.assertLessEqual(len(selected), 4)

        for item in selected:
            self.assertIn("selection_rank", item)
            self.assertIn(item["selection_reason"], {"in_window_ranked_selection", "fallback_recent_pre_window"})

        self.assertTrue(any(row.get("reason_code") == "domain_cap_exceeded" for row in excluded))


if __name__ == "__main__":
    unittest.main()
