#!/usr/bin/env python3
"""Render artifacts/last_run.json into a concise markdown summary."""

from __future__ import annotations

import argparse
import json
import pathlib


def _as_code(value):
    if value is None:
        return "`n/a`"
    return f"`{value}`"


def render(summary: dict) -> str:
    lines = [
        "# Weekly Pipeline Run Summary",
        "",
        f"- Issue ID: {_as_code(summary.get('issue_id'))}",
        f"- Pipeline status: {_as_code(summary.get('pipeline_status'))}",
        f"- Artifact check: {_as_code(summary.get('artifact_check'))}",
        f"- Source audit: {_as_code(summary.get('source_candidate_audit'))}",
        f"- Buttondown: {_as_code(summary.get('buttondown'))}",
        f"- Run started: {_as_code(summary.get('run_started_at'))}",
        f"- Run finished: {_as_code(summary.get('run_finished_at'))}",
        f"- Run duration (s): {_as_code(summary.get('run_duration_seconds'))}",
        "",
        "## Step timings",
        "",
    ]

    steps = summary.get("step_results") or []
    if not steps:
        lines.append("- No step results recorded.")
    else:
        for step in steps:
            lines.append(
                "- "
                f"{step.get('name', 'unknown')}: "
                f"status={_as_code(step.get('status'))}, "
                f"duration={_as_code(step.get('duration_seconds'))}, "
                f"started={_as_code(step.get('started_at'))}, "
                f"finished={_as_code(step.get('finished_at'))}"
            )

    output_artifact_checks = summary.get("output_artifact_checks") or {}
    lines.extend(["", "## Output artifacts", ""])
    if output_artifact_checks:
        for label, detail in output_artifact_checks.items():
            path = detail.get("path")
            exists = detail.get("exists")
            status = "present" if exists else "missing"
            lines.append(f"- {label}: `{status}` — `{path}`")
    else:
        lines.append("- None recorded")

    missing = summary.get("missing_artifacts") or []
    lines.extend(["", "## Missing artifacts", ""])
    if missing:
        lines.extend([f"- `{path}`" for path in missing])
    else:
        lines.append("- None")

    failed_step = summary.get("failed_step")
    lines.extend(["", "## Failed step detail", ""])
    if failed_step:
        lines.append(f"- Name: {_as_code(failed_step.get('name'))}")
        lines.append(f"- Exit code: {_as_code(failed_step.get('exit_code'))}")
        lines.append(f"- Command: {_as_code(failed_step.get('command'))}")
    else:
        lines.append("- None")

    run_history = summary.get("run_history")
    lines.extend(["", "## Run history snapshot", ""])
    if isinstance(run_history, dict):
        lines.append(f"- JSON snapshot: {_as_code(run_history.get('json'))}")
        lines.append(f"- Markdown snapshot: {_as_code(run_history.get('markdown'))}")
        lines.append(f"- Retention limit: {_as_code(run_history.get('retention_limit'))}")
        lines.append(f"- Index JSON: {_as_code(run_history.get('index_json'))}")
        lines.append(f"- Index markdown: {_as_code(run_history.get('index_markdown'))}")
        lines.append(f"- Retained run snapshot count: {_as_code(run_history.get('retained_run_count'))}")
        lines.append(f"- Retained JSON snapshot count: {_as_code(run_history.get('retained_json_count'))}")
        lines.append(f"- Retained markdown snapshot count: {_as_code(run_history.get('retained_markdown_count'))}")
        lines.append(f"- Orphan JSON snapshot count: {_as_code(run_history.get('orphan_json_count'))}")
        lines.append(f"- Orphan markdown snapshot count: {_as_code(run_history.get('orphan_markdown_count'))}")
    else:
        lines.append("- Not recorded")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="artifacts/last_run.json", help="Path to run summary JSON")
    parser.add_argument("--output", default="artifacts/last_run.md", help="Path to markdown output")
    args = parser.parse_args()

    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    summary = json.loads(input_path.read_text(encoding="utf-8"))
    markdown = render(summary)
    output_path.write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    main()
