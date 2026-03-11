#!/usr/bin/env python3
"""Astro-first release audit checks for Microsoft Agentic AI Weekly.

Checks:
1) Canonical latest issue path is consistent across home, archive, and RSS.
2) Legacy root HTML routes and legacy post HTML files redirect to canonical Astro paths.
3) Internal links in site/dist resolve to existing generated files.
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys
import xml.etree.ElementTree as ET


REDIRECT_RE = re.compile(r"window\.location\.replace\('([^']+)'\)")
ISSUE_LINK_RE = re.compile(r'href="(/posts/issue-[^"/\s]+)"')
HREF_SRC_RE = re.compile(r'(?:href|src)="([^"]+)"')

LEGACY_ROOT_REDIRECTS = {
    "about.html": "/about",
    "archive.html": "/archive",
    "corrections.html": "/corrections",
    "sources.html": "/sources",
}


def _parse_issue_meta(issue_path: pathlib.Path):
    raw = issue_path.read_text(encoding="utf-8")
    status_match = re.search(r"^status:\s*(.+)$", raw, flags=re.MULTILINE)
    slug_match = re.search(r"^slug:\s*(.+)$", raw, flags=re.MULTILINE)
    published_match = re.search(r'^published_at:\s*"([^"]+)"', raw, flags=re.MULTILINE)

    status = status_match.group(1).strip().strip('"').strip("'").lower() if status_match else "draft"
    slug = slug_match.group(1).strip().strip('"').strip("'") if slug_match else issue_path.stem
    published_raw = published_match.group(1).strip() if published_match else ""
    try:
        published = dt.datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
    except Exception:
        published = dt.datetime.min.replace(tzinfo=dt.timezone.utc)
    return {"status": status, "slug": slug, "published_at": published}


def latest_published_slug(root: pathlib.Path) -> str:
    issues_dir = root / "site" / "src" / "content" / "issues"
    metas = []
    for issue_file in issues_dir.glob("*.md"):
        meta = _parse_issue_meta(issue_file)
        if meta["status"] == "published":
            metas.append(meta)
    if not metas:
        return ""
    metas.sort(key=lambda row: row["published_at"], reverse=True)
    return metas[0]["slug"]


def extract_first_issue_link(html_text: str) -> str:
    match = ISSUE_LINK_RE.search(html_text)
    return match.group(1) if match else ""


def extract_latest_feed_issue_path(feed_path: pathlib.Path) -> str:
    tree = ET.parse(feed_path)
    channel = tree.getroot().find("channel")
    if channel is None:
        return ""
    first_item = channel.find("item")
    if first_item is None:
        return ""
    link = first_item.findtext("link", default="").strip()
    marker = "/posts/issue-"
    idx = link.find(marker)
    if idx < 0:
        return ""
    value = link[idx:]
    return value.rstrip("/")


def resolve_internal_target(dist_root: pathlib.Path, source_file: pathlib.Path, raw_target: str) -> pathlib.Path | None:
    target = raw_target.strip()
    if not target or target.startswith(("http://", "https://", "mailto:", "tel:", "data:", "#")):
        return None
    target = target.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None

    if target.startswith("/"):
        path = dist_root / target.lstrip("/")
    else:
        path = source_file.parent / target

    if path.exists():
        return path
    if path.is_dir():
        index_file = path / "index.html"
        if index_file.exists():
            return index_file
    if path.suffix == "":
        index_file = dist_root / target.lstrip("/") / "index.html" if target.startswith("/") else source_file.parent / target / "index.html"
        if index_file.exists():
            return index_file
    return path


def check_internal_links(dist_root: pathlib.Path) -> list[str]:
    missing = []
    for html_file in dist_root.rglob("*.html"):
        text = html_file.read_text(encoding="utf-8")
        for raw in HREF_SRC_RE.findall(text):
            resolved = resolve_internal_target(dist_root, html_file, raw)
            if resolved is None:
                continue
            if not resolved.exists():
                rel_file = html_file.relative_to(dist_root).as_posix()
                missing.append(f"{rel_file} -> {raw}")
    return missing


def redirect_target(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = REDIRECT_RE.search(text)
    return match.group(1) if match else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Astro release audit checks")
    parser.add_argument("--root", default=".", help="Project root path")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    dist = root / "site" / "dist"
    index_html = dist / "index.html"
    archive_html = dist / "archive" / "index.html"
    feed_xml = dist / "feed.xml"

    required = [index_html, archive_html, feed_xml]
    missing_required = [path for path in required if not path.exists()]
    if missing_required:
        print("Missing required generated files:")
        for path in missing_required:
            print(f"- {path}")
        print("Run `npm run site:build` before release_audit.")
        return 1

    latest_slug = latest_published_slug(root)
    latest_path = f"/posts/{latest_slug}" if latest_slug else ""

    home_latest = extract_first_issue_link(index_html.read_text(encoding="utf-8"))
    archive_latest = extract_first_issue_link(archive_html.read_text(encoding="utf-8"))
    feed_latest = extract_latest_feed_issue_path(feed_xml)

    parity_errors = []
    if not latest_path:
        parity_errors.append("No published issue slug found in site/src/content/issues")
    else:
        if home_latest != latest_path:
            parity_errors.append(f"home latest mismatch: expected {latest_path}, got {home_latest or 'none'}")
        if archive_latest != latest_path:
            parity_errors.append(f"archive latest mismatch: expected {latest_path}, got {archive_latest or 'none'}")
        if feed_latest != latest_path:
            parity_errors.append(f"feed latest mismatch: expected {latest_path}, got {feed_latest or 'none'}")
        expected_issue_file = dist / latest_path.lstrip("/") / "index.html"
        if not expected_issue_file.exists():
            parity_errors.append(f"latest issue page missing in dist: {expected_issue_file}")

    legacy_errors = []
    for filename, expected in LEGACY_ROOT_REDIRECTS.items():
        path = root / filename
        if not path.exists():
            legacy_errors.append(f"missing legacy route shim: {filename}")
            continue
        actual = redirect_target(path)
        if actual != expected:
            legacy_errors.append(f"{filename} redirect mismatch: expected {expected}, got {actual or 'none'}")

    for post_file in sorted((root / "posts").glob("issue-*.html")):
        slug = post_file.stem
        expected = f"/posts/{slug}"
        actual = redirect_target(post_file)
        if actual != expected:
            legacy_errors.append(
                f"posts/{post_file.name} redirect mismatch: expected {expected}, got {actual or 'none'}"
            )

    missing_links = check_internal_links(dist)

    print(f"Latest published slug: {latest_slug or 'none'}")
    print(f"Home latest: {home_latest or 'none'}")
    print(f"Archive latest: {archive_latest or 'none'}")
    print(f"Feed latest: {feed_latest or 'none'}")
    print(f"Legacy redirect errors: {legacy_errors or 'none'}")
    print(f"Missing internal dist links: {missing_links or 'none'}")

    if parity_errors:
        print("\nParity errors:")
        for error in parity_errors:
            print(f"- {error}")

    if parity_errors or legacy_errors or missing_links:
        return 1

    print("Release audit OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
