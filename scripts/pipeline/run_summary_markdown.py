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
