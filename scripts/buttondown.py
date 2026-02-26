#!/usr/bin/env python3
import argparse
import json
import os
import pathlib
import sys
import urllib.request
import urllib.error

BASE_URL = "https://api.buttondown.email/v1"


def _api_key() -> str:
    key = os.getenv("BUTTONDOWN_API_KEY", "").strip()
    if not key:
        print("Missing BUTTONDOWN_API_KEY", file=sys.stderr)
        sys.exit(1)
    return key


def _request(method: str, path: str, data: dict | None = None):
    url = f"{BASE_URL}{path}"
    body = None
    headers = {
        "Authorization": f"Token {_api_key()}",
        "Accept": "application/json",
    }
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode("utf-8")
            return resp.status, json.loads(text) if text else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="ignore")
        print(f"HTTP {e.code}: {err}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args):
    status, payload = _request("GET", "/emails")
    results = payload.get("results", [])
    if args.status:
        results = [r for r in results if r.get("status") == args.status]
    for r in results[: args.limit]:
        print(f"{r.get('id')}\t{r.get('status')}\t{r.get('subject')}")
    print(f"\nTotal matched: {len(results)}")


def cmd_create(args):
    body = pathlib.Path(args.body_file).read_text(encoding="utf-8")
    payload = {
        "subject": args.subject,
        "body": body,
        "email_type": "newsletter",
    }
    if args.description:
        payload["description"] = args.description

    _, created = _request("POST", "/emails", payload)
    print("Draft created")
    print(f"ID: {created.get('id')}")
    print(f"Status: {created.get('status')}")
    print(f"URL: {created.get('absolute_url')}")


def cmd_get(args):
    _, payload = _request("GET", f"/emails/{args.email_id}")
    print(json.dumps(payload, indent=2))


def main():
    p = argparse.ArgumentParser(description="Buttondown helper for Microsoft Agentic AI Weekly")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List emails")
    p_list.add_argument("--status", default="", help="Filter by status (e.g. draft, sent)")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.set_defaults(func=cmd_list)

    p_create = sub.add_parser("create", help="Create draft from markdown/text file")
    p_create.add_argument("--subject", required=True)
    p_create.add_argument("--body-file", required=True)
    p_create.add_argument("--description", default="")
    p_create.set_defaults(func=cmd_create)

    p_get = sub.add_parser("get", help="Get full email JSON by id")
    p_get.add_argument("email_id")
    p_get.set_defaults(func=cmd_get)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
