#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib
import shutil
import subprocess
import time

from issue_id_guard import validate_issue_id

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)
RUN_HISTORY_DIR = ART / "run_history"
RUN_HISTORY_DIR.mkdir(exist_ok=True)
RUN_HISTORY_LIMIT = 30
RUN_HISTORY_INDEX_JSON = RUN_HISTORY_DIR / "index.json"
RUN_HISTORY_INDEX_MARKDOWN = RUN_HISTORY_DIR / "index.md"


def issue_id_today():
    now = dt.datetime.utcnow()
    y, w, _ = now.isocalendar()
    return f"{y}-{w:02d}"


def _artifact_exists(path_str):
    path = ROOT / path_str
    return path.exists()


def _validate_issue_id(issue_id):
    try:
        validate_issue_id(issue_id)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def _build_output_artifacts(issue_id):
    return {
        "queue_json": f"artifacts/editorial_queue-{issue_id}.json",
        "queue_markdown": f"artifacts/editorial_queue-{issue_id}.md",
        "run_report": f"artifacts/run_report-{issue_id}.md",
        "issue_markdown": f"posts/issue-{issue_id}.md",
        "issue_html": f"posts/issue-{issue_id}.html",
        "email_draft": f"drafts/email-{issue_id}.md",
        "source_audit_json": "artifacts/source_candidate_audit.json",
        "source_audit_markdown": "artifacts/source_candidate_audit.md",
        "buttondown_drafts": "artifacts/buttondown_drafts.json",
        "run_summary_json": "artifacts/last_run.json",
        "run_summary_markdown": "artifacts/last_run.md",
        "run_history_index_json": "artifacts/run_history/index.json",
        "run_history_index_markdown": "artifacts/run_history/index.md",
    }


def _run_step(label, command):
    started_at = dt.datetime.utcnow()
    started_monotonic = time.monotonic()
    subprocess.check_call(command)
    finished_at = dt.datetime.utcnow()
    return {
        "name": label,
        "status": "ok",
        "command": command,
        "started_at": started_at.isoformat() + "Z",
        "finished_at": finished_at.isoformat() + "Z",
        "duration_seconds": round(time.monotonic() - started_monotonic, 3),
    }


def _history_stem(path):
    if path.suffix in {".json", ".md"}:
        return path.name[: -len(path.suffix)]
    return path.stem


def _collect_history_runs():
    files = sorted(RUN_HISTORY_DIR.glob("last_run-*"), key=lambda p: p.stat().st_mtime, reverse=True)
    runs = {}
    for path in files:
        stem = _history_stem(path)
        entry = runs.setdefault(stem, {"stem": stem, "json": None, "md": None, "mtime": 0.0})
        if path.suffix == ".json":
            entry["json"] = path
        elif path.suffix == ".md":
            entry["md"] = path
        entry["mtime"] = max(entry["mtime"], path.stat().st_mtime)

    return sorted(runs.values(), key=lambda item: item["mtime"], reverse=True)


def _write_run_history_index(retained_runs):
    index_payload = {
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "retention_limit": RUN_HISTORY_LIMIT,
        "retained_run_count": len(retained_runs),
        "runs": [
            {
                "stem": run["stem"],
                "json": str(run["json"].relative_to(ROOT)) if run["json"] else None,
                "markdown": str(run["md"].relative_to(ROOT)) if run["md"] else None,
                "mtime": run["mtime"],
                "mtime_iso": dt.datetime.utcfromtimestamp(run["mtime"]).isoformat() + "Z",
            }
            for run in retained_runs
        ],
    }

    RUN_HISTORY_INDEX_JSON.write_text(json.dumps(index_payload, indent=2), encoding="utf-8")

    lines = [
        "# Run History Index",
        "",
        f"- Generated at: `{index_payload['generated_at']}`",
        f"- Retention limit: `{RUN_HISTORY_LIMIT}`",
        f"- Retained runs: `{len(retained_runs)}`",
        "",
        "## Snapshots",
        "",
    ]

    if not retained_runs:
        lines.append("- None")
    else:
        for run in retained_runs:
            json_path = str(run["json"].relative_to(ROOT)) if run["json"] else "n/a"
            markdown_path = str(run["md"].relative_to(ROOT)) if run["md"] else "n/a"
            lines.append(f"- `{run['stem']}`")
            lines.append(f"  - json: `{json_path}`")
            lines.append(f"  - markdown: `{markdown_path}`")
            lines.append(f"  - mtime: `{dt.datetime.utcfromtimestamp(run['mtime']).isoformat()}Z`")

    RUN_HISTORY_INDEX_MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_run_history_snapshot(issue_id, run_finished_at):
    stamp = run_finished_at.strftime("%Y%m%dT%H%M%SZ")

    attempt = 0
    while True:
        suffix = "" if attempt == 0 else f"-{attempt:02d}"
        json_name = f"last_run-{issue_id}-{stamp}{suffix}.json"
        md_name = f"last_run-{issue_id}-{stamp}{suffix}.md"
        history_json = RUN_HISTORY_DIR / json_name
        history_md = RUN_HISTORY_DIR / md_name
        if not history_json.exists() and not history_md.exists():
            break
        attempt += 1

    shutil.copy2(ART / "last_run.json", history_json)
    shutil.copy2(ART / "last_run.md", history_md)

    history_runs = _collect_history_runs()
    for stale_run in history_runs[RUN_HISTORY_LIMIT:]:
        if stale_run["json"]:
            stale_run["json"].unlink()
        if stale_run["md"]:
            stale_run["md"].unlink()

    retained_runs = _collect_history_runs()[:RUN_HISTORY_LIMIT]
    retained_json_count = sum(1 for run in retained_runs if run["json"])
    retained_markdown_count = sum(1 for run in retained_runs if run["md"])

    _write_run_history_index(retained_runs)

    return {
        "json": str(history_json.relative_to(ROOT)),
        "markdown": str(history_md.relative_to(ROOT)),
        "index_json": str(RUN_HISTORY_INDEX_JSON.relative_to(ROOT)),
        "index_markdown": str(RUN_HISTORY_INDEX_MARKDOWN.relative_to(ROOT)),
        "retention_limit": RUN_HISTORY_LIMIT,
        "retained_run_count": len(retained_runs),
        "retained_json_count": retained_json_count,
        "retained_markdown_count": retained_markdown_count,
        "orphan_json_count": max(0, retained_json_count - retained_markdown_count),
        "orphan_markdown_count": max(0, retained_markdown_count - retained_json_count),
    }


def run(issue_id=None, skip_buttondown=False, skip_source_audit=False, enforce_artifacts=True):
    issue_id = issue_id or issue_id_today()

    run_started_at = dt.datetime.utcnow()
    run_started_monotonic = time.monotonic()

    pipeline_status = "ok"
    failed_step = None
    step_results = []

    _validate_issue_id(issue_id)

    output_artifacts = _build_output_artifacts(issue_id)

    required_artifacts = [
        output_artifacts["queue_json"],
        output_artifacts["queue_markdown"],
        output_artifacts["run_report"],
        output_artifacts["issue_markdown"],
        output_artifacts["issue_html"],
        output_artifacts["email_draft"],
    ]

    if not skip_source_audit:
        required_artifacts.extend([
            output_artifacts["source_audit_json"],
            output_artifacts["source_audit_markdown"],
        ])

    source_audit_status = "skipped"
    buttondown_status = "skipped"

    core_steps = [
        ("build_queue", ["python3", str(ROOT / "scripts/pipeline/build_queue.py"), "--issue-id", issue_id]),
        ("validate_queue", ["python3", str(ROOT / "scripts/pipeline/validate_queue.py"), "--issue-id", issue_id]),
        ("generate_issue", ["python3", str(ROOT / "scripts/pipeline/generate_issue.py"), "--issue-id", issue_id]),
        ("render_issue_html", ["python3", str(ROOT / "scripts/pipeline/render_issue_html.py"), "--issue-id", issue_id]),
        ("run_report", ["python3", str(ROOT / "scripts/pipeline/run_report.py"), "--issue-id", issue_id]),
    ]

    try:
        for label, command in core_steps:
            step_results.append(_run_step(label, command))

        if not skip_source_audit:
            command = ["python3", str(ROOT / "scripts/pipeline/source_candidate_audit.py")]
            started_at = dt.datetime.utcnow()
            started_monotonic = time.monotonic()
            rc = subprocess.call(command)
            finished_at = dt.datetime.utcnow()
            source_audit_status = "ok" if rc == 0 else f"failed_exit_{rc}"
            step_results.append({
                "name": "source_candidate_audit",
                "status": source_audit_status,
                "command": command,
                "started_at": started_at.isoformat() + "Z",
                "finished_at": finished_at.isoformat() + "Z",
                "duration_seconds": round(time.monotonic() - started_monotonic, 3),
            })

        draft_path = ROOT / "drafts" / f"email-{issue_id}.md"
        if draft_path.exists() and not skip_buttondown:
            command = [
                "python3",
                str(ROOT / "scripts/pipeline/buttondown_draft.py"),
                "--issue-id",
                issue_id,
                "--subject",
                f"Microsoft Agentic AI Weekly — Issue {issue_id}",
                "--body-file",
                str(draft_path),
            ]
            started_at = dt.datetime.utcnow()
            started_monotonic = time.monotonic()
            rc = subprocess.call(command)
            finished_at = dt.datetime.utcnow()
            buttondown_status = "ok" if rc == 0 else f"failed_exit_{rc}"
            step_results.append({
                "name": "buttondown_draft",
                "status": buttondown_status,
                "command": command,
                "started_at": started_at.isoformat() + "Z",
                "finished_at": finished_at.isoformat() + "Z",
                "duration_seconds": round(time.monotonic() - started_monotonic, 3),
            })

    except subprocess.CalledProcessError as exc:
        pipeline_status = "failed"
        failed_step = {
            "name": core_steps[len(step_results)][0] if len(step_results) < len(core_steps) else "unknown",
            "command": exc.cmd,
            "exit_code": exc.returncode,
        }
        failed_at = dt.datetime.utcnow()
        step_results.append({
            "name": failed_step["name"],
            "status": f"failed_exit_{exc.returncode}",
            "command": exc.cmd,
            "started_at": None,
            "finished_at": failed_at.isoformat() + "Z",
            "duration_seconds": None,
        })

    artifact_checks = {path: _artifact_exists(path) for path in required_artifacts}
    output_artifact_checks = {
        label: {
            "path": path,
            "exists": _artifact_exists(path),
        }
        for label, path in output_artifacts.items()
    }
    missing_artifacts = [path for path, exists in artifact_checks.items() if not exists]

    run_finished_at = dt.datetime.utcnow()

    summary = {
        "issue_id": issue_id,
        "generated_at": run_finished_at.isoformat() + "Z",
        "run_started_at": run_started_at.isoformat() + "Z",
        "run_finished_at": run_finished_at.isoformat() + "Z",
        "run_duration_seconds": round(time.monotonic() - run_started_monotonic, 3),
        "pipeline_status": pipeline_status,
        "failed_step": failed_step,
        "step_results": step_results,
        "buttondown": buttondown_status,
        "source_candidate_audit": source_audit_status,
        "artifact_check": "ok" if not missing_artifacts else "missing_artifacts",
        "missing_artifacts": missing_artifacts,
        "artifacts": required_artifacts,
        "artifact_checks": artifact_checks,
        "output_artifacts": output_artifacts,
        "output_artifact_checks": output_artifact_checks,
        "enforce_artifacts": enforce_artifacts,
    }

    def write_latest_summary_files(summary_payload):
        (ART / "last_run.json").write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
        markdown_rc_local = subprocess.call([
            "python3",
            str(ROOT / "scripts/pipeline/run_summary_markdown.py"),
            "--input",
            str(ART / "last_run.json"),
            "--output",
            str(ART / "last_run.md"),
        ])
        if markdown_rc_local != 0:
            print("warning: failed to render artifacts/last_run.md from last_run.json")
            return False
        return True

    rendered_markdown = write_latest_summary_files(summary)
    run_history = None
    if rendered_markdown:
        run_history = _write_run_history_snapshot(issue_id, run_finished_at)

    summary["run_history"] = run_history
    summary["output_artifact_checks"] = {
        label: {
            "path": path,
            "exists": _artifact_exists(path),
        }
        for label, path in output_artifacts.items()
    }
    write_latest_summary_files(summary)

    print(json.dumps(summary, indent=2))

    if pipeline_status != "ok":
        raise SystemExit("Weekly pipeline failed before completion. See artifacts/last_run.json for diagnostics.")

    if enforce_artifacts and missing_artifacts:
        raise SystemExit(
            "Missing required weekly artifacts: " + ", ".join(missing_artifacts)
        )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue-id", help="Override ISO week issue id (YYYY-WW).")
    ap.add_argument("--skip-buttondown", action="store_true", help="Generate site/email artifacts without Buttondown draft API call.")
    ap.add_argument("--skip-source-audit", action="store_true", help="Skip source candidate feed health audit artifact generation.")
    ap.add_argument("--no-enforce-artifacts", action="store_true", help="Do not fail the run when required output artifacts are missing.")
    args = ap.parse_args()
    run(
        issue_id=args.issue_id,
        skip_buttondown=args.skip_buttondown,
        skip_source_audit=args.skip_source_audit,
        enforce_artifacts=not args.no_enforce_artifacts,
    )
