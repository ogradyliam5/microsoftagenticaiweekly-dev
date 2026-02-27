#!/usr/bin/env python3
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


def run():
    issue_id = issue_id_today()
    subprocess.check_call(["python3", str(ROOT / "scripts/pipeline/build_queue.py"), "--issue-id", issue_id])
    subprocess.check_call(["python3", str(ROOT / "scripts/pipeline/generate_issue.py"), "--issue-id", issue_id])

    draft_path = ROOT / "drafts" / f"email-{issue_id}.md"
    if draft_path.exists():
        subprocess.call([
            "python3", str(ROOT / "scripts/pipeline/buttondown_draft.py"),
            "--issue-id", issue_id,
            "--subject", f"Microsoft Agentic AI Weekly — Issue {issue_id}",
            "--body-file", str(draft_path)
        ])

    summary = {
        "issue_id": issue_id,
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "artifacts": [
            f"artifacts/editorial_queue-{issue_id}.json",
            f"artifacts/editorial_queue-{issue_id}.md",
            f"posts/issue-{issue_id}.md",
            f"drafts/email-{issue_id}.md"
        ]
    }
    (ART / "last_run.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
