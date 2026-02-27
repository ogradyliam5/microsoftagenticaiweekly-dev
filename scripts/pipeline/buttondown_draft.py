#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
STATE = ROOT / "artifacts" / "buttondown_drafts.json"


def api(method, path, token, payload=None):
    url = f"https://api.buttondown.email/v1{path}"
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Token {token}")
    req.add_header("Accept", "application/json")
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        txt = r.read().decode("utf-8")
        return json.loads(txt) if txt else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue-id", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--body-file", required=True)
    args = ap.parse_args()

    token = os.getenv("BUTTONDOWN_API_KEY", "").strip()
    if not token:
        print("BUTTONDOWN_API_KEY missing; skipped")
        return

    body = pathlib.Path(args.body_file).read_text(encoding="utf-8")
    payload = {
        "subject": args.subject,
        "body": body,
        "email_type": "newsletter",
        "description": f"Draft for issue {args.issue_id} (approval required)",
    }

    created = api("POST", "/emails", token, payload)

    STATE.parent.mkdir(exist_ok=True)
    state = {}
    if STATE.exists():
        state = json.loads(STATE.read_text(encoding="utf-8"))
    state[args.issue_id] = {
        "draft_id": created.get("id"),
        "absolute_url": created.get("absolute_url", ""),
        "updated_at": dt.datetime.utcnow().isoformat() + "Z"
    }
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state[args.issue_id], indent=2))


if __name__ == "__main__":
    main()
