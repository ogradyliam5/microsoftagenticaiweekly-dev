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


def _load_json(path: pathlib.Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Failed to parse JSON at {path}: {exc}") from exc


def _validate_run_history_index(summary, run_history):
    index_json_rel = run_history.get("index_json")
    index_markdown_rel = run_history.get("index_markdown")
    snapshot_json_rel = run_history.get("json")
    snapshot_markdown_rel = run_history.get("markdown")

    _assert(isinstance(index_json_rel, str) and index_json_rel, "run_history.index_json must be a non-empty string")
    _assert(isinstance(index_markdown_rel, str) and index_markdown_rel, "run_history.index_markdown must be a non-empty string")

    output_artifacts = summary.get("output_artifacts") or {}
    _assert(output_artifacts.get("run_history_index_json") == index_json_rel, "run_history.index_json must match output_artifacts.run_history_index_json")
    _assert(output_artifacts.get("run_history_index_markdown") == index_markdown_rel, "run_history.index_markdown must match output_artifacts.run_history_index_markdown")

    index_json_path = ROOT / index_json_rel
    index_markdown_path = ROOT / index_markdown_rel
    _assert(index_json_path.exists(), f"Run-history index JSON missing: {index_json_rel}")
    _assert(index_markdown_path.exists(), f"Run-history index markdown missing: {index_markdown_rel}")

    index_payload = _load_json(index_json_path)
    for key in ("generated_at", "retention_limit", "retained_run_count", "runs"):
        _assert(key in index_payload, f"run-history index missing key: {key}")

    runs = index_payload["runs"]
    _assert(isinstance(runs, list), "run-history index runs must be an array")
    _assert(index_payload["retained_run_count"] == len(runs), "run-history index retained_run_count must equal len(runs)")

    previous_mtime = None
    seen_stems = set()
    for idx, run in enumerate(runs):
        _assert(isinstance(run, dict), f"run-history index runs[{idx}] must be an object")
        stem = run.get("stem")
        _assert(isinstance(stem, str) and stem, f"run-history index runs[{idx}].stem must be a non-empty string")
        _assert(stem not in seen_stems, f"run-history index contains duplicate stem: {stem}")
        seen_stems.add(stem)

        mtime = run.get("mtime")
        _assert(isinstance(mtime, (int, float)), f"run-history index runs[{idx}].mtime must be numeric")
        mtime_iso = run.get("mtime_iso")
        _assert(isinstance(mtime_iso, str) and mtime_iso, f"run-history index runs[{idx}].mtime_iso must be a non-empty string")

        if previous_mtime is not None:
            _assert(previous_mtime >= mtime, "run-history index runs must be sorted by mtime descending")
        previous_mtime = mtime

        json_rel = run.get("json")
        markdown_rel = run.get("markdown")
        if json_rel is not None:
            _assert((ROOT / json_rel).exists(), f"run-history index JSON snapshot missing on disk: {json_rel}")
        if markdown_rel is not None:
            _assert((ROOT / markdown_rel).exists(), f"run-history index markdown snapshot missing on disk: {markdown_rel}")

    retained_limit = run_history.get("retention_limit")
    retained_run_count = run_history.get("retained_run_count")
    retained_json_count = run_history.get("retained_json_count")
    retained_markdown_count = run_history.get("retained_markdown_count")
    orphan_json_count = run_history.get("orphan_json_count")
    orphan_markdown_count = run_history.get("orphan_markdown_count")

    _assert(index_payload["retention_limit"] == retained_limit, "run_history retention_limit mismatch with index")
    _assert(retained_run_count == len(runs), "run_history.retained_run_count mismatch with index runs length")

    json_paths = {run.get("json") for run in runs if run.get("json")}
    markdown_paths = {run.get("markdown") for run in runs if run.get("markdown")}

    _assert(snapshot_json_rel in json_paths, "run_history.json snapshot not found in run-history index")
    _assert(snapshot_markdown_rel in markdown_paths, "run_history.markdown snapshot not found in run-history index")

    if runs:
        latest_entry = runs[0]
        _assert(
            latest_entry.get("json") == snapshot_json_rel,
            "run_history.index latest JSON snapshot must match run_history.json",
        )
        _assert(
            latest_entry.get("markdown") == snapshot_markdown_rel,
            "run_history.index latest markdown snapshot must match run_history.markdown",
        )

    _assert(retained_json_count == len(json_paths), "run_history.retained_json_count mismatch with run-history index")
    _assert(retained_markdown_count == len(markdown_paths), "run_history.retained_markdown_count mismatch with run-history index")

    computed_orphan_json = max(0, len(json_paths) - len(markdown_paths))
    computed_orphan_markdown = max(0, len(markdown_paths) - len(json_paths))
    _assert(orphan_json_count == computed_orphan_json, "run_history.orphan_json_count mismatch")
    _assert(orphan_markdown_count == computed_orphan_markdown, "run_history.orphan_markdown_count mismatch")


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
        _validate_run_history_index(summary, run_history)


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
