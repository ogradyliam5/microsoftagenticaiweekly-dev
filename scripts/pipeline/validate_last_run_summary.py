#!/usr/bin/env python3
"""Validate artifacts/last_run.json contract and artifact-check parity."""

import argparse
import datetime as dt
import json
import pathlib
import re
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

DURATION_TOLERANCE_SECONDS = 5.0


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


def _parse_utc_timestamp(value, field_name):
    _assert(isinstance(value, str) and value, f"{field_name} must be a non-empty string")
    _assert(value.endswith("Z"), f"{field_name} must end with 'Z'")
    try:
        return dt.datetime.fromisoformat(value[:-1])
    except ValueError as exc:
        raise ValidationError(f"{field_name} must be valid ISO-8601 UTC timestamp: {value}") from exc


def _parse_run_history_snapshot_path(path_value, field_name):
    _assert(isinstance(path_value, str) and path_value, f"{field_name} must be a non-empty string")
    name = pathlib.Path(path_value).name
    match = re.fullmatch(r"last_run-(.+)-(\d{8}T\d{6}Z)(?:-(\d{2}))?\.(json|md)", name)
    _assert(match is not None, f"{field_name} has unexpected snapshot filename format: {path_value}")
    issue_id, stamp, suffix, extension = match.groups()
    try:
        stamp_dt = dt.datetime.strptime(stamp, "%Y%m%dT%H%M%SZ")
    except ValueError as exc:
        raise ValidationError(f"{field_name} has invalid snapshot timestamp: {path_value}") from exc
    return {
        "issue_id": issue_id,
        "stamp": stamp,
        "stamp_dt": stamp_dt,
        "suffix": suffix or "",
        "extension": extension,
        "name": name,
    }


def _validate_step_results(step_results, run_started_at, run_finished_at):
    _assert(isinstance(step_results, list), "step_results must be an array")
    previous_finished_at = None
    for idx, step in enumerate(step_results):
        _assert(isinstance(step, dict), f"step_results[{idx}] must be an object")
        for key in ("name", "status", "command", "started_at", "finished_at", "duration_seconds"):
            _assert(key in step, f"step_results[{idx}] missing key: {key}")

        status = step["status"]
        started_at_raw = step["started_at"]
        finished_at_raw = step["finished_at"]
        duration = step["duration_seconds"]

        is_failed = isinstance(status, str) and status.startswith("failed_exit_")
        if is_failed:
            _assert(started_at_raw is None or isinstance(started_at_raw, str), f"step_results[{idx}].started_at must be null/string for failed steps")
            started_at = None
            if isinstance(started_at_raw, str):
                started_at = _parse_utc_timestamp(started_at_raw, f"step_results[{idx}].started_at")
            finished_at = _parse_utc_timestamp(finished_at_raw, f"step_results[{idx}].finished_at")
            _assert(finished_at >= run_started_at, f"step_results[{idx}].finished_at must be >= run_started_at")
            _assert(finished_at <= run_finished_at, f"step_results[{idx}].finished_at must be <= run_finished_at")
            if previous_finished_at is not None:
                _assert(finished_at >= previous_finished_at, f"step_results[{idx}].finished_at must be >= previous step finished_at")
            if started_at is not None:
                _assert(started_at >= run_started_at, f"step_results[{idx}].started_at must be >= run_started_at")
                _assert(started_at <= run_finished_at, f"step_results[{idx}].started_at must be <= run_finished_at")
                _assert(finished_at >= started_at, f"step_results[{idx}] finished_at must be >= started_at")
            _assert(duration is None or isinstance(duration, (int, float)), f"step_results[{idx}].duration_seconds must be null/numeric for failed steps")
            if isinstance(duration, (int, float)):
                _assert(duration >= 0, f"step_results[{idx}].duration_seconds must be >= 0")
                if started_at is not None:
                    expected_duration = (finished_at - started_at).total_seconds()
                    _assert(
                        abs(duration - expected_duration) <= DURATION_TOLERANCE_SECONDS,
                        f"step_results[{idx}].duration_seconds must be within {DURATION_TOLERANCE_SECONDS}s of finished_at-started_at",
                    )
            previous_finished_at = finished_at
            continue

        started_at = _parse_utc_timestamp(started_at_raw, f"step_results[{idx}].started_at")
        finished_at = _parse_utc_timestamp(finished_at_raw, f"step_results[{idx}].finished_at")
        _assert(started_at >= run_started_at, f"step_results[{idx}].started_at must be >= run_started_at")
        _assert(started_at <= run_finished_at, f"step_results[{idx}].started_at must be <= run_finished_at")
        _assert(finished_at >= run_started_at, f"step_results[{idx}].finished_at must be >= run_started_at")
        _assert(finished_at <= run_finished_at, f"step_results[{idx}].finished_at must be <= run_finished_at")
        if previous_finished_at is not None:
            _assert(started_at >= previous_finished_at, f"step_results[{idx}].started_at must be >= previous step finished_at")
            _assert(finished_at >= previous_finished_at, f"step_results[{idx}].finished_at must be >= previous step finished_at")
        _assert(finished_at >= started_at, f"step_results[{idx}] finished_at must be >= started_at")
        _assert(isinstance(duration, (int, float)), f"step_results[{idx}].duration_seconds must be numeric")
        _assert(duration >= 0, f"step_results[{idx}].duration_seconds must be >= 0")
        expected_duration = (finished_at - started_at).total_seconds()
        _assert(
            abs(duration - expected_duration) <= DURATION_TOLERANCE_SECONDS,
            f"step_results[{idx}].duration_seconds must be within {DURATION_TOLERANCE_SECONDS}s of finished_at-started_at",
        )
        previous_finished_at = finished_at


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

    _parse_utc_timestamp(index_payload["generated_at"], "run-history index generated_at")

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
        mtime_dt = _parse_utc_timestamp(mtime_iso, f"run-history index runs[{idx}].mtime_iso")

        expected_mtime_dt = dt.datetime.fromtimestamp(mtime, dt.timezone.utc).replace(tzinfo=None)
        _assert(
            abs((expected_mtime_dt - mtime_dt).total_seconds()) <= 1.0,
            f"run-history index runs[{idx}].mtime_iso must match mtime within 1 second",
        )

        if previous_mtime is not None:
            _assert(previous_mtime >= mtime, "run-history index runs must be sorted by mtime descending")
        previous_mtime = mtime

        json_rel = run.get("json")
        markdown_rel = run.get("markdown")
        if json_rel is not None:
            _assert(json_rel.startswith("artifacts/run_history/last_run-"), f"run-history index JSON snapshot path has unexpected prefix: {json_rel}")
            _assert((ROOT / json_rel).exists(), f"run-history index JSON snapshot missing on disk: {json_rel}")
        if markdown_rel is not None:
            _assert(markdown_rel.startswith("artifacts/run_history/last_run-"), f"run-history index markdown snapshot path has unexpected prefix: {markdown_rel}")
            _assert((ROOT / markdown_rel).exists(), f"run-history index markdown snapshot missing on disk: {markdown_rel}")

        if json_rel and markdown_rel:
            json_stem = pathlib.Path(json_rel).stem
            markdown_stem = pathlib.Path(markdown_rel).stem
            _assert(json_stem == markdown_stem == stem, f"run-history index runs[{idx}] json/markdown stems must match stem")

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

    snapshot_json_meta = _parse_run_history_snapshot_path(snapshot_json_rel, "run_history.json")
    snapshot_markdown_meta = _parse_run_history_snapshot_path(snapshot_markdown_rel, "run_history.markdown")

    _assert(snapshot_json_meta["extension"] == "json", "run_history.json must point to a .json snapshot")
    _assert(snapshot_markdown_meta["extension"] == "md", "run_history.markdown must point to a .md snapshot")
    _assert(snapshot_json_meta["issue_id"] == summary["issue_id"], "run_history.json snapshot issue-id must match summary.issue_id")
    _assert(snapshot_markdown_meta["issue_id"] == summary["issue_id"], "run_history.markdown snapshot issue-id must match summary.issue_id")
    _assert(snapshot_json_meta["stamp"] == snapshot_markdown_meta["stamp"], "run_history snapshot JSON/markdown timestamps must match")
    _assert(snapshot_json_meta["suffix"] == snapshot_markdown_meta["suffix"], "run_history snapshot JSON/markdown suffixes must match")

    generated_at = _parse_utc_timestamp(summary["generated_at"], "generated_at")
    run_finished_at = _parse_utc_timestamp(summary["run_finished_at"], "run_finished_at")
    _assert(snapshot_json_meta["stamp_dt"] <= generated_at, "run_history snapshot timestamp must be <= generated_at")
    _assert(snapshot_json_meta["stamp_dt"] <= run_finished_at, "run_history snapshot timestamp must be <= run_finished_at")

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

    generated_at = _parse_utc_timestamp(summary["generated_at"], "generated_at")
    run_started_at = _parse_utc_timestamp(summary["run_started_at"], "run_started_at")
    run_finished_at = _parse_utc_timestamp(summary["run_finished_at"], "run_finished_at")
    _assert(run_finished_at >= run_started_at, "run_finished_at must be >= run_started_at")
    _assert(generated_at >= run_started_at, "generated_at must be >= run_started_at")

    run_duration_seconds = summary["run_duration_seconds"]
    _assert(isinstance(run_duration_seconds, (int, float)), "run_duration_seconds must be numeric")
    _assert(run_duration_seconds >= 0, "run_duration_seconds must be >= 0")
    expected_run_duration = (run_finished_at - run_started_at).total_seconds()
    _assert(
        abs(run_duration_seconds - expected_run_duration) <= DURATION_TOLERANCE_SECONDS,
        f"run_duration_seconds must be within {DURATION_TOLERANCE_SECONDS}s of run_finished_at-run_started_at",
    )

    _assert(summary["pipeline_status"] in {"ok", "failed"}, "pipeline_status must be 'ok' or 'failed'")

    step_results = summary["step_results"]
    _validate_step_results(step_results, run_started_at, run_finished_at)

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

    _assert(
        "curation_manifest_json" in output_artifacts,
        "output_artifacts must include curation_manifest_json",
    )
    curation_manifest_path = output_artifacts.get("curation_manifest_json")
    _assert(
        isinstance(curation_manifest_path, str) and curation_manifest_path.startswith("artifacts/curation_manifest-"),
        "output_artifacts.curation_manifest_json has unexpected format",
    )

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
