#!/usr/bin/env python3
"""Validate external source links referenced by published Astro issues."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import socket
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from typing import Dict, List


ROOT = pathlib.Path(__file__).resolve().parents[2]
ISSUES_DIR = ROOT / "site" / "src" / "content" / "issues"
DEFAULT_JSON = ROOT / "artifacts" / "link_validation.json"
DEFAULT_MD = ROOT / "artifacts" / "link_validation.md"

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
STATUS_RE = re.compile(r"^status:\s*(.+)$", re.MULTILINE)
SLUG_RE = re.compile(r"^slug:\s*(.+)$", re.MULTILINE)


def parse_frontmatter_value(pattern: re.Pattern[str], text: str, default: str = "") -> str:
    match = pattern.search(text)
    if not match:
        return default
    return match.group(1).strip().strip('"').strip("'")


def extract_issue_links(path: pathlib.Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    status = parse_frontmatter_value(STATUS_RE, raw, "draft").lower()
    slug = parse_frontmatter_value(SLUG_RE, raw, path.stem)

    links = []
    for match in LINK_RE.findall(raw):
        url = match.strip().strip("<>").split()[0]
        if url.startswith(("http://", "https://")):
            links.append(url)

    return {
        "file": str(path.relative_to(ROOT)).replace("\\", "/"),
        "slug": slug,
        "status": status,
        "links": links,
    }


def http_check(url: str, timeout: int) -> dict:
    headers = {"User-Agent": "maiw-link-validator/1.0"}
    req = urllib.request.Request(url, method="HEAD", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            code = int(response.status)
            return {"url": url, "ok": code < 400, "kind": "ok", "status_code": code, "error": ""}
    except urllib.error.HTTPError as exc:
        # Some publishers reject HEAD but allow GET.
        req_get = urllib.request.Request(url, method="GET", headers=headers)
        try:
            with urllib.request.urlopen(req_get, timeout=timeout) as response:
                status_code = int(response.status)
                return {
                    "url": url,
                    "ok": status_code < 400,
                    "kind": "ok" if status_code < 400 else "error",
                    "status_code": status_code,
                    "error": "",
                }
        except urllib.error.HTTPError as get_exc:
            get_code = int(getattr(get_exc, "code", 0) or 0)
            return {
                "url": url,
                "ok": False,
                "kind": "warning" if get_code in {403, 429} else "error",
                "status_code": get_code,
                "error": str(get_exc),
            }
        except Exception as get_exc:
            return {
                "url": url,
                "ok": False,
                "kind": "warning" if _is_timeout_error(get_exc) else "error",
                "status_code": None,
                "error": str(get_exc),
            }
    except Exception as exc:
        return {
            "url": url,
            "ok": False,
            "kind": "warning" if _is_timeout_error(exc) else "error",
            "status_code": None,
            "error": str(exc),
        }


def _is_timeout_error(exc: Exception) -> bool:
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return True
    if isinstance(exc, urllib.error.URLError):
        reason = getattr(exc, "reason", None)
        if isinstance(reason, (TimeoutError, socket.timeout)):
            return True
        if isinstance(reason, str) and "timed out" in reason.lower():
            return True
    return "timed out" in str(exc).lower()


def markdown_report(result: dict) -> str:
    lines: List[str] = [
        "# Issue Link Validation",
        "",
        f"- Total unique links: `{result['summary']['total']}`",
        f"- OK: `{result['summary']['ok']}`",
        f"- Warning: `{result['summary']['warning']}`",
        f"- Error: `{result['summary']['error']}`",
        "",
    ]

    if result["summary"]["error"] == 0 and result["summary"]["warning"] == 0:
        lines.append("All validated links returned healthy responses.")
        lines.append("")

    lines.append("## By Issue")
    lines.append("")
    for issue in result["issues"]:
        lines.append(f"- `{issue['slug']}` (`{issue['status']}`): {len(issue['links'])} link(s)")
    lines.append("")

    lines.append("## Link Results")
    lines.append("")
    for row in result["checks"]:
        status_code = row["status_code"] if row["status_code"] is not None else "n/a"
        lines.append(f"- [{row['kind'].upper()}] `{status_code}` {row['url']}")
        if row["issues"]:
            lines.append(f"  - issues: {', '.join(row['issues'])}")
        if row["error"]:
            lines.append(f"  - error: {row['error']}")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate external source links in published issue content.")
    parser.add_argument("--json-out", default=str(DEFAULT_JSON), help="Output JSON artifact path")
    parser.add_argument("--md-out", default=str(DEFAULT_MD), help="Output markdown artifact path")
    parser.add_argument("--timeout", type=int, default=12, help="HTTP request timeout in seconds")
    parser.add_argument("--include-drafts", action="store_true", help="Include draft/scheduled issues in validation")
    parser.add_argument("--allow-warnings", action="store_true", help="Do not fail when only warnings are present")
    args = parser.parse_args()

    issues = []
    for issue_file in sorted(ISSUES_DIR.glob("*.md")):
        issue = extract_issue_links(issue_file)
        if not args.include_drafts and issue["status"] != "published":
            continue
        issues.append(issue)

    url_to_issues: Dict[str, set] = defaultdict(set)
    for issue in issues:
        for url in issue["links"]:
            url_to_issues[url].add(issue["slug"])

    checks = []
    for url in sorted(url_to_issues):
        row = http_check(url, timeout=args.timeout)
        row["issues"] = sorted(url_to_issues[url])
        checks.append(row)

    summary = {
        "total": len(checks),
        "ok": sum(1 for row in checks if row["kind"] == "ok"),
        "warning": sum(1 for row in checks if row["kind"] == "warning"),
        "error": sum(1 for row in checks if row["kind"] == "error"),
    }

    result = {
        "generated_at": dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z"),
        "issues": issues,
        "checks": checks,
        "summary": summary,
    }

    json_out = pathlib.Path(args.json_out)
    md_out = pathlib.Path(args.md_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    md_out.write_text(markdown_report(result), encoding="utf-8")

    print(json.dumps(summary, indent=2))

    if summary["error"] > 0:
        return 1
    if summary["warning"] > 0 and not args.allow_warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
