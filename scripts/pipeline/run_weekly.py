#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)


def issue_id_today():
    now = dt.datetime.utcnow()
    y, w, _ = now.isocalendar()
    return f"{y}-{w:02d}"


def run(issue_id=None, skip_buttondown=False):
    issue_id = issue_id or issue_id_today()
    subprocess.check_call(["python3", str(ROOT / "scripts/pipeline/build_queue.py"), "--issue-id", issue_id])
    subprocess.check_call(["python3", str(ROOT / "scripts/pipeline/validate_queue.py"), "--issue-id", issue_id])
    subprocess.check_call(["python3", str(ROOT / "scripts/pipeline/generate_issue.py"), "--issue-id", issue_id])
    subprocess.check_call(["python3", str(ROOT / "scripts/pipeline/render_issue_html.py"), "--issue-id", issue_id])

    draft_path = ROOT / "drafts" / f"email-{issue_id}.md"
    buttondown_status = "skipped"
    if draft_path.exists() and not skip_buttondown:
        rc = subprocess.call([
            "python3", str(ROOT / "scripts/pipeline/buttondown_draft.py"),
            "--issue-id", issue_id,
            "--subject", f"Microsoft Agentic AI Weekly — Issue {issue_id}",
            "--body-file", str(draft_path)
        ])
        buttondown_status = "ok" if rc == 0 else f"failed_exit_{rc}"

    summary = {
        "issue_id": issue_id,
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "buttondown": buttondown_status,
        "artifacts": [
            f"artifacts/editorial_queue-{issue_id}.json",
            f"artifacts/editorial_queue-{issue_id}.md",
            f"posts/issue-{issue_id}.md",
            f"posts/issue-{issue_id}.html",
            f"drafts/email-{issue_id}.md"
        ]
    }
    (ART / "last_run.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue-id", help="Override ISO week issue id (YYYY-WW).")
    ap.add_argument("--skip-buttondown", action="store_true", help="Generate site/email artifacts without Buttondown draft API call.")
    args = ap.parse_args()
    run(issue_id=args.issue_id, skip_buttondown=args.skip_buttondown)
