#!/usr/bin/env python3
"""Validate artifacts/last_run.json contract and artifact-check parity."""

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT / "artifacts" / "last_run.json"

REQUIRED_TOP_LEVEL_KEYS = [
    "issue_id",
    "generated_at",
    "run_started_at",
    "run_finished_at",
    "run_duration_seconds",
    "pipeline_status",
    "step_results",
    "artifact_check",
    "missing_artifacts",
    "artifacts",
    "artifact_checks",
    "output_artifacts",
    "output_artifact_checks",
    "enforce_artifacts",
    "run_history",
]


class ValidationError(ValueError):
    pass


def _assert(condition, message):
    if not condition:
        raise ValidationError(message)


def validate(summary):
    for key in REQUIRED_TOP_LEVEL_KEYS:
        _assert(key in summary, f"Missing top-level key: {key}")

    _assert(summary["pipeline_status"] in {"ok", "failed"}, "pipeline_status must be 'ok' or 'failed'")

    step_results = summary["step_results"]
    _assert(isinstance(step_results, list), "step_results must be an array")
    for idx, step in enumerate(step_results):
        _assert(isinstance(step, dict), f"step_results[{idx}] must be an object")
        for key in ("name", "status", "command", "started_at", "finished_at", "duration_seconds"):
            _assert(key in step, f"step_results[{idx}] missing key: {key}")

    artifacts = summary["artifacts"]
    artifact_checks = summary["artifact_checks"]
    _assert(isinstance(artifacts, list), "artifacts must be an array")
    _assert(isinstance(artifact_checks, dict), "artifact_checks must be an object")

    for path in artifacts:
        _assert(path in artifact_checks, f"artifact_checks missing required path: {path}")

    missing = sorted(path for path in artifacts if artifact_checks.get(path) is False)
    _assert(sorted(summary["missing_artifacts"]) == missing, "missing_artifacts must match artifact_checks false entries")

    expected_artifact_check = "ok" if not missing else "missing_artifacts"
    _assert(summary["artifact_check"] == expected_artifact_check, "artifact_check inconsistent with artifact_checks")

    output_artifacts = summary["output_artifacts"]
    output_artifact_checks = summary["output_artifact_checks"]
    _assert(isinstance(output_artifacts, dict), "output_artifacts must be an object")
    _assert(isinstance(output_artifact_checks, dict), "output_artifact_checks must be an object")

    for label, path in output_artifacts.items():
        _assert(label in output_artifact_checks, f"output_artifact_checks missing label: {label}")
        detail = output_artifact_checks[label]
        _assert(isinstance(detail, dict), f"output_artifact_checks[{label}] must be an object")
        _assert(detail.get("path") == path, f"output_artifact_checks[{label}].path mismatch")
        _assert(isinstance(detail.get("exists"), bool), f"output_artifact_checks[{label}].exists must be boolean")

    run_history = summary["run_history"]
    _assert(run_history is None or isinstance(run_history, dict), "run_history must be null or an object")
    if isinstance(run_history, dict):
        for key in (
            "json",
            "markdown",
            "index_json",
            "index_markdown",
            "retention_limit",
            "retained_run_count",
            "retained_json_count",
            "retained_markdown_count",
            "orphan_json_count",
            "orphan_markdown_count",
        ):
            _assert(key in run_history, f"run_history missing key: {key}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_PATH), help="Path to last_run.json")
    args = parser.parse_args()

    input_path = pathlib.Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Run summary not found: {input_path}")

    try:
        summary = json.loads(input_path.read_text(encoding="utf-8"))
        validate(summary)
    except (json.JSONDecodeError, ValidationError) as exc:
        print(f"last_run summary validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"last_run summary validation passed: {input_path}")


if __name__ == "__main__":
    main()
