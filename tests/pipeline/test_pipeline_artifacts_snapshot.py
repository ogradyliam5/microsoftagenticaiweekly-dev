import json
import pathlib
import subprocess
import sys
import unittest
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]

QUEUE_PATH = ROOT / "artifacts" / "editorial_queue-000.json"
MANIFEST_PATH = ROOT / "artifacts" / "curation_manifest-000.json"
POST_MD_PATH = ROOT / "posts" / "issue-000.md"
POST_HTML_PATH = ROOT / "posts" / "issue-000.html"
EMAIL_MD_PATH = ROOT / "drafts" / "email-000.md"
def _extract_redirect_target(content):
    marker = "window.location.replace('"
    idx = content.find(marker)
    if idx < 0:
        return None
    start = idx + len(marker)
    end = content.find("'", start)
    if end < 0:
        return None
    return content[start:end]


class PipelineArtifactsSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        commands = [
            [sys.executable, str(ROOT / "scripts" / "pipeline" / "make_sample_issue000.py")],
            [sys.executable, str(ROOT / "scripts" / "pipeline" / "validate_queue.py"), "--issue-id", "000"],
            [sys.executable, str(ROOT / "scripts" / "pipeline" / "generate_issue.py"), "--issue-id", "000"],
            [sys.executable, str(ROOT / "scripts" / "pipeline" / "render_issue_html.py"), "--issue-id", "000"],
            [sys.executable, str(ROOT / "scripts" / "pipeline" / "run_report.py"), "--issue-id", "000"],
        ]
        for command in commands:
            subprocess.run(command, check=True, cwd=ROOT)

        if not QUEUE_PATH.exists():
            raise unittest.SkipTest(f"Missing fixture: {QUEUE_PATH}")
        if not MANIFEST_PATH.exists():
            raise unittest.SkipTest(f"Missing fixture: {MANIFEST_PATH}")

        cls.queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_contract_versions_are_v2(self):
        self.assertEqual(self.queue.get("contract_version"), "v2")
        self.assertEqual(self.manifest.get("contract_version"), "v2")

    def test_selected_item_ids_match_queue_item_ids(self):
        queue_ids = [item["id"] for item in self.queue.get("items", [])]
        manifest_ids = self.manifest.get("selected_item_ids", [])
        self.assertEqual(queue_ids, manifest_ids)

    def test_reason_counts_match_excluded_items(self):
        excluded = self.manifest.get("excluded_items", [])
        expected = Counter(item.get("reason_code", "unknown") for item in excluded)
        self.assertEqual(dict(expected), self.manifest.get("reason_counts", {}))

    def test_domain_cap_respected_or_explicit_override_enabled(self):
        cap = self.queue.get("quality_summary", {}).get("domain_cap", 2)
        items = self.queue.get("items", [])
        counts = Counter(item.get("domain", "unknown") for item in items)
        cap_exceeded = any(count > cap for count in counts.values())
        if cap_exceeded:
            override = self.queue.get("composition", {}).get("override") or {}
            self.assertTrue(override.get("enabled") is True)
        else:
            self.assertTrue(all(count <= cap for count in counts.values()))

    def test_rendered_outputs_include_canonical_story_fields(self):
        for path in (POST_MD_PATH, EMAIL_MD_PATH):
            if not path.exists():
                self.skipTest(f"Missing rendered output: {path}")
            content = path.read_text(encoding="utf-8")
            self.assertIn("Signal", content)
            self.assertIn("Mini-abstract", content)
            self.assertIn("Why click", content)
            self.assertIn("Source confidence", content)

        if not POST_HTML_PATH.exists():
            self.skipTest(f"Missing rendered output: {POST_HTML_PATH}")
        html_content = POST_HTML_PATH.read_text(encoding="utf-8")
        self.assertIn("Moved: Microsoft Agentic AI Weekly", html_content)
        self.assertEqual(_extract_redirect_target(html_content), "/posts/issue-000")

    def test_legacy_route_shims_redirect_to_canonical_paths(self):
        expected = {
            "archive.html": "/archive",
            "about.html": "/about",
            "corrections.html": "/corrections",
            "sources.html": "/sources",
        }
        for name, target in expected.items():
            page = ROOT / name
            if not page.exists():
                self.skipTest(f"Missing legacy route shim: {page}")
            content = page.read_text(encoding="utf-8")
            self.assertEqual(_extract_redirect_target(content), target)


if __name__ == "__main__":
    unittest.main()
