#!/usr/bin/env python3
"""Release audit checks for Microsoft Agentic AI Weekly static site.

Checks:
1) Internal local href/src links resolve to existing files.
2) RSS feed parses and includes every published issue page listed in archive.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT_HTML = ["index.html", "archive.html", "about.html", "sources.html", "corrections.html"]
HREF_SRC_RE = re.compile(r'(?:href|src)="([^"]+)"')
ISSUE_LINK_RE = re.compile(r'href="(posts/issue-[0-9]+(?:-[0-9]+)?\.html)"')


def html_files(root: Path) -> list[Path]:
    files = []
    for name in ROOT_HTML:
        p = root / name
        if p.exists():
            files.append(p)
    files.extend(sorted((root / "posts").glob("issue-*.html")))
    return files


def normalize_target(ref: str) -> str | None:
    ref = ref.strip()
    if not ref or ref.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
        return None
    return ref.split("#", 1)[0].split("?", 1)[0]


def check_internal_links(root: Path, files: list[Path]) -> list[str]:
    missing: list[str] = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        for raw in HREF_SRC_RE.findall(text):
            rel = normalize_target(raw)
            if not rel:
                continue
            target = (root / rel).resolve() if rel.startswith("/") else (f.parent / rel).resolve()
            if rel.startswith("/"):
                target = (root / rel.lstrip("/")).resolve()
            if not target.exists():
                missing.append(f"{f.relative_to(root)} -> {raw}")
    return missing


def archive_issue_slugs(root: Path) -> set[str]:
    archive = root / "archive.html"
    if not archive.exists():
        return set()
    text = archive.read_text(encoding="utf-8")
    return {Path(p).stem for p in ISSUE_LINK_RE.findall(text)}


def feed_issue_slugs(root: Path) -> set[str]:
    feed = root / "feed.xml"
    if not feed.exists():
        raise FileNotFoundError("feed.xml not found")
    tree = ET.parse(feed)
    channel = tree.getroot().find("channel")
    if channel is None:
        return set()
    slugs = set()
    for item in channel.findall("item"):
        link = item.findtext("link", default="")
        if "/posts/" in link and link.endswith(".html"):
            slugs.add(Path(link).stem)
    return slugs


def published_issue_slugs(root: Path) -> set[str]:
    return {p.stem for p in (root / "posts").glob("issue-*.html")}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run static release audit checks")
    parser.add_argument("--root", default=".", help="Project root path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = html_files(root)

    missing_links = check_internal_links(root, files)
    archive_slugs = archive_issue_slugs(root)
    feed_slugs = feed_issue_slugs(root)
    published_slugs = published_issue_slugs(root)

    archive_missing = sorted(published_slugs - archive_slugs)
    feed_missing = sorted(published_slugs - feed_slugs)

    print(f"Audited HTML files: {len(files)}")
    print(f"Published issues: {len(published_slugs)}")

    if missing_links:
        print("\nMissing internal links:")
        for x in missing_links:
            print(f"- {x}")

    print(f"Archive missing issues: {archive_missing or 'none'}")
    print(f"Feed missing issues: {feed_missing or 'none'}")

    if missing_links or archive_missing or feed_missing:
        return 1

    print("Release audit OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
