import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "pipeline"))

import run_weekly  # noqa: E402


class RunWeeklyContractUnitTests(unittest.TestCase):
    def test_output_artifacts_include_v2_manifest(self):
        artifacts = run_weekly._build_output_artifacts("2026-10")
        self.assertIn("curation_manifest_json", artifacts)
        self.assertEqual(artifacts["curation_manifest_json"], "artifacts/curation_manifest-2026-10.json")

    def test_relpath_uses_posix_separator(self):
        nested = ROOT / "artifacts" / "run_history" / "index.json"
        rel = run_weekly._relpath(nested)
        self.assertEqual(rel, "artifacts/run_history/index.json")
        self.assertNotIn("\\", rel)


if __name__ == "__main__":
    unittest.main()
