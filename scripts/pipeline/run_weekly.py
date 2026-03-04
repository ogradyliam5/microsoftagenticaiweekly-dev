#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib
import subprocess
import time

from issue_id_guard import validate_issue_id

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)


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


def run(issue_id=None, skip_buttondown=False, skip_source_audit=False, enforce_artifacts=True):
    issue_id = issue_id or issue_id_today()

    run_started_at = dt.datetime.utcnow()
    run_started_monotonic = time.monotonic()

    pipeline_status = "ok"
    failed_step = None
    step_results = []

    _validate_issue_id(issue_id)

    required_artifacts = [
        f"artifacts/editorial_queue-{issue_id}.json",
        f"artifacts/editorial_queue-{issue_id}.md",
        f"artifacts/run_report-{issue_id}.md",
        f"posts/issue-{issue_id}.md",
        f"posts/issue-{issue_id}.html",
        f"drafts/email-{issue_id}.md",
    ]

    if not skip_source_audit:
        required_artifacts.extend([
            "artifacts/source_candidate_audit.json",
            "artifacts/source_candidate_audit.md",
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
        "enforce_artifacts": enforce_artifacts,
    }
    (ART / "last_run.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    markdown_rc = subprocess.call([
        "python3",
        str(ROOT / "scripts/pipeline/run_summary_markdown.py"),
        "--input",
        str(ART / "last_run.json"),
        "--output",
        str(ART / "last_run.md"),
    ])
    if markdown_rc != 0:
        print("warning: failed to render artifacts/last_run.md from last_run.json")

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
