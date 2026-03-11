#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import pathlib
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
STATE = pathlib.Path(
    os.getenv("BUTTONDOWN_DRAFT_STATE_PATH", str(ROOT / "artifacts" / "buttondown_drafts.json"))
)
API_BASE = os.getenv("BUTTONDOWN_API_BASE_URL", "https://api.buttondown.email/v1").rstrip("/")


def log(level, message, **fields):
    event = {"level": level, "message": message}
    event.update(fields)
    print(json.dumps(event, ensure_ascii=False))


def read_http_error(err):
    body = ""
    try:
        body = err.read().decode("utf-8", errors="replace")
    except Exception:
        body = ""

    parsed = None
    if body:
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = None

    return {
        "code": getattr(err, "code", None),
        "reason": getattr(err, "reason", ""),
        "body": body,
        "json": parsed,
    }


def api(method, path, token, payload=None):
    url = f"{API_BASE}{path}"
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Token {token}")
    req.add_header("Accept", "application/json")
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        txt = r.read().decode("utf-8")
        return json.loads(txt) if txt else {}


def list_drafts(token, subject=None, limit=100):
    params = {"status": "draft", "page_size": min(max(limit, 1), 100)}
    if subject:
        params["subject"] = subject

    path = f"/emails?{urllib.parse.urlencode(params)}"
    payload = api("GET", path, token)

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ("results", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return value

    return []


def find_draft_by_subject(token, subject):
    drafts = list_drafts(token, subject=subject)
    for draft in drafts:
        if str(draft.get("subject", "")).strip() == subject:
            return draft
    return None


def load_state():
    if not STATE.exists():
        return {}
    return json.loads(STATE.read_text(encoding="utf-8"))


def save_state(state):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue-id", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--body-file", required=True)
    args = ap.parse_args()

    token = os.getenv("BUTTONDOWN_API_KEY", "").strip()
    if not token:
        log("warn", "BUTTONDOWN_API_KEY missing; skipping draft sync", issue_id=args.issue_id)
        return

    body = pathlib.Path(args.body_file).read_text(encoding="utf-8")

    create_payload = {
        "subject": args.subject,
        "body": body,
    }
    update_payload = {
        "subject": args.subject,
        "body": body,
    }

    state = load_state()
    existing_draft_id = str(state.get(args.issue_id, {}).get("draft_id", "")).strip()

    created_or_updated = None
    action = "created"

    try:
        if existing_draft_id:
            try:
                created_or_updated = api("PATCH", f"/emails/{existing_draft_id}", token, update_payload)
                action = "updated"
            except urllib.error.HTTPError as e:
                detail = read_http_error(e)

                if e.code in (404, 422):
                    log(
                        "warn",
                        "Stored Buttondown draft id unusable; attempting subject-based recovery",
                        issue_id=args.issue_id,
                        draft_id=existing_draft_id,
                        http_code=detail["code"],
                        response=detail["json"] if detail["json"] is not None else detail["body"][:400],
                    )

                    matched = find_draft_by_subject(token, args.subject)
                    if matched and matched.get("id"):
                        matched_id = str(matched.get("id"))
                        created_or_updated = api("PATCH", f"/emails/{matched_id}", token, update_payload)
                        action = "recovered_by_subject"
                    else:
                        created_or_updated = api("POST", "/emails", token, create_payload)
                        action = "recreated"
                else:
                    raise
        else:
            matched = find_draft_by_subject(token, args.subject)
            if matched and matched.get("id"):
                matched_id = str(matched.get("id"))
                created_or_updated = api("PATCH", f"/emails/{matched_id}", token, update_payload)
                action = "updated_existing_by_subject"
            else:
                created_or_updated = api("POST", "/emails", token, create_payload)
                action = "created"
    except urllib.error.HTTPError as e:
        detail = read_http_error(e)

        if e.code == 422:
            matched = find_draft_by_subject(token, args.subject)
            if matched and matched.get("id"):
                try:
                    matched_id = str(matched.get("id"))
                    created_or_updated = api("PATCH", f"/emails/{matched_id}", token, update_payload)
                    action = "recovered_after_create_422"
                except Exception as patch_error:
                    log(
                        "error",
                        "Buttondown 422 recovery patch failed",
                        issue_id=args.issue_id,
                        existing_draft_id=existing_draft_id,
                        matched_draft_id=matched.get("id"),
                        error=str(patch_error),
                        action="continuing_without_email_draft",
                    )
                    return
            else:
                log(
                    "error",
                    "Buttondown draft sync failed (422 and no matching draft found)",
                    issue_id=args.issue_id,
                    existing_draft_id=existing_draft_id,
                    http_code=detail["code"],
                    reason=str(detail["reason"]),
                    response=detail["json"] if detail["json"] is not None else detail["body"][:600],
                    action="continuing_without_email_draft",
                )
                return
        else:
            log(
                "error",
                "Buttondown draft sync failed",
                issue_id=args.issue_id,
                existing_draft_id=existing_draft_id,
                http_code=detail["code"],
                reason=str(detail["reason"]),
                response=detail["json"] if detail["json"] is not None else detail["body"][:600],
                action="continuing_without_email_draft",
            )
            return
    except Exception as e:
        log(
            "error",
            "Unexpected Buttondown draft sync error",
            issue_id=args.issue_id,
            existing_draft_id=existing_draft_id,
            error=str(e),
            action="continuing_without_email_draft",
        )
        return

    state[args.issue_id] = {
        "draft_id": created_or_updated.get("id"),
        "absolute_url": created_or_updated.get("absolute_url", ""),
        "updated_at": dt.datetime.utcnow().isoformat() + "Z",
        "action": action,
    }
    save_state(state)
    log("info", "Buttondown draft sync complete", issue_id=args.issue_id, **state[args.issue_id])


if __name__ == "__main__":
    main()
