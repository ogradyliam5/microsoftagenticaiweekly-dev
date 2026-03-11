import copy
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "pipeline"))

import validate_last_run_summary  # noqa: E402


def _valid_summary():
    return {
        "issue_id": "2026-10",
        "generated_at": "2026-03-07T12:00:05Z",
        "run_started_at": "2026-03-07T12:00:00Z",
        "run_finished_at": "2026-03-07T12:00:05Z",
        "run_duration_seconds": 5.0,
        "pipeline_status": "ok",
        "step_results": [],
        "artifact_check": "ok",
        "missing_artifacts": [],
        "artifacts": [],
        "artifact_checks": {},
        "output_artifacts": {
            "curation_manifest_json": "artifacts/curation_manifest-2026-10.json",
        },
        "output_artifact_checks": {
            "curation_manifest_json": {
                "path": "artifacts/curation_manifest-2026-10.json",
                "exists": False,
            }
        },
        "enforce_artifacts": True,
        "run_history": None,
    }


class ValidateLastRunSummaryUnitTests(unittest.TestCase):
    def test_valid_summary_passes(self):
        validate_last_run_summary.validate(_valid_summary())

    def test_missing_curation_manifest_output_fails(self):
        summary = _valid_summary()
        summary["output_artifacts"] = {}
        summary["output_artifact_checks"] = {}
        with self.assertRaises(validate_last_run_summary.ValidationError):
            validate_last_run_summary.validate(summary)

    def test_inconsistent_duration_fails(self):
        summary = _valid_summary()
        summary["run_duration_seconds"] = 1000
        with self.assertRaises(validate_last_run_summary.ValidationError):
            validate_last_run_summary.validate(summary)

    def test_mismatch_output_artifact_check_path_fails(self):
        summary = _valid_summary()
        bad = copy.deepcopy(summary)
        bad["output_artifact_checks"]["curation_manifest_json"]["path"] = "artifacts/other.json"
        with self.assertRaises(validate_last_run_summary.ValidationError):
            validate_last_run_summary.validate(bad)


if __name__ == "__main__":
    unittest.main()
