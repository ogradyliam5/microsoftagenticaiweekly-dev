#!/usr/bin/env python3
"""Release audit checks for Microsoft Agentic AI Weekly static site.

Checks:
1) Internal local href/src links resolve to existing files.
2) RSS feed parses and includes every published issue page listed in archive.
"""

from __future__ import annotations

import argparse
from email.utils import parsedate_to_datetime
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT_HTML = ["index.html", "archive.html", "about.html", "sources.html", "corrections.html"]
HREF_SRC_RE = re.compile(r'(?:href|src)="([^"]+)"')
ISSUE_LINK_RE = re.compile(r'href="(posts/issue-[0-9]+(?:-[0-9]+)?\.html)"')
INDEX_LATEST_LINK_RE = re.compile(
    r'<a\b[^>]*href="(posts/issue-[0-9]+(?:-[0-9]+)?\.html)"[^>]*>([^<]*latest edition[^<]*)</a>',
    re.IGNORECASE,
)
HOMEPAGE_LATEST_CARD_RE = re.compile(
    r'<article\b[^>]*>.*?<p[^>]*>\s*Start here\s*[·\-]\s*Latest edition\s*</p>.*?<a[^>]*href="(posts/issue-[0-9]+(?:-[0-9]+)?\.html)"',
    re.IGNORECASE | re.DOTALL,
)
HOMEPAGE_LATEST_CARD_META_RE = re.compile(
    r'<article\b[^>]*>.*?<p[^>]*>\s*Start here\s*[·\-]\s*Latest edition\s*</p>\s*<p[^>]*>([^<]+)</p>',
    re.IGNORECASE | re.DOTALL,
)
HOMEPAGE_FRESHNESS_LINE_RE = re.compile(r'<p[^>]*>\s*Latest:\s*([^<]+)</p>', re.IGNORECASE)


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


def latest_feed_item_metadata(root: Path) -> dict[str, str] | None:
    feed = root / "feed.xml"
    if not feed.exists():
        raise FileNotFoundError("feed.xml not found")
    tree = ET.parse(feed)
    channel = tree.getroot().find("channel")
    if channel is None:
        return None
    first_item = channel.find("item")
    if first_item is None:
        return None

    link = first_item.findtext("link", default="")
    slug = Path(link).stem if "/posts/" in link and link.endswith(".html") else ""

    title = first_item.findtext("title", default="").strip()
    week_label = title.split("—", 1)[0].strip() if title else ""

    pub_date = first_item.findtext("pubDate", default="").strip()
    full_date = ""
    if pub_date:
        dt = parsedate_to_datetime(pub_date)
        full_date = dt.strftime("%A, %d %B %Y")

    return {"slug": slug, "week_label": week_label, "full_date": full_date}


def published_issue_slugs(root: Path) -> set[str]:
    return {p.stem for p in (root / "posts").glob("issue-*.html")}


def index_latest_links(root: Path) -> list[tuple[str, str]]:
    index = root / "index.html"
    if not index.exists():
        return []
    text = index.read_text(encoding="utf-8")
    matches: list[tuple[str, str]] = []
    for href, label in INDEX_LATEST_LINK_RE.findall(text):
        matches.append((Path(href).stem, " ".join(label.split())))
    return matches


def index_latest_card_slugs(root: Path) -> list[str]:
    index = root / "index.html"
    if not index.exists():
        return []
    text = index.read_text(encoding="utf-8")
    return [Path(href).stem for href in HOMEPAGE_LATEST_CARD_RE.findall(text)]


def index_latest_card_meta_lines(root: Path) -> list[str]:
    index = root / "index.html"
    if not index.exists():
        return []
    text = index.read_text(encoding="utf-8")
    return [" ".join(line.split()) for line in HOMEPAGE_LATEST_CARD_META_RE.findall(text)]


def index_hero_freshness_line(root: Path) -> str | None:
    index = root / "index.html"
    if not index.exists():
        return None
    text = index.read_text(encoding="utf-8")
    match = HOMEPAGE_FRESHNESS_LINE_RE.search(text)
    if not match:
        return None
    return " ".join(match.group(1).split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Run static release audit checks")
    parser.add_argument("--root", default=".", help="Project root path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = html_files(root)

    missing_links = check_internal_links(root, files)
    archive_slugs = archive_issue_slugs(root)
    feed_slugs = feed_issue_slugs(root)
    latest_item = latest_feed_item_metadata(root)
    published_slugs = published_issue_slugs(root)
    latest_links = index_latest_links(root)
    latest_card_slugs = index_latest_card_slugs(root)
    latest_card_meta_lines = index_latest_card_meta_lines(root)
    hero_freshness_line = index_hero_freshness_line(root)

    archive_missing = sorted(published_slugs - archive_slugs)
    feed_missing = sorted(published_slugs - feed_slugs)
    archive_stale = sorted(archive_slugs - published_slugs)
    feed_stale = sorted(feed_slugs - published_slugs)

    latest_link_errors: list[str] = []
    latest_card_errors: list[str] = []
    freshness_errors: list[str] = []
    latest_feed_slug = latest_item["slug"] if latest_item else ""
    expected_week_label = latest_item["week_label"] if latest_item else ""
    expected_full_date = latest_item["full_date"] if latest_item else ""

    if latest_feed_slug:
        if not latest_links:
            latest_link_errors.append("index.html has no 'latest edition' links")
        for slug, label in latest_links:
            if slug != latest_feed_slug:
                latest_link_errors.append(
                    f"index.html latest-edition link '{label}' points to {slug}, expected {latest_feed_slug}"
                )

        if len(latest_card_slugs) != 1:
            latest_card_errors.append(
                "index.html must include exactly one 'Start here · Latest edition' card marker"
            )
        for slug in latest_card_slugs:
            if slug != latest_feed_slug:
                latest_card_errors.append(
                    f"index.html latest-edition card points to {slug}, expected {latest_feed_slug}"
                )

        if len(latest_card_meta_lines) != 1:
            latest_card_errors.append(
                "index.html latest-edition card must include exactly one metadata date line"
            )
        for meta_line in latest_card_meta_lines:
            if expected_week_label and expected_week_label not in meta_line:
                latest_card_errors.append(
                    f"index.html latest-edition card metadata missing week label '{expected_week_label}'"
                )
            if expected_full_date and expected_full_date not in meta_line:
                latest_card_errors.append(
                    f"index.html latest-edition card metadata missing date '{expected_full_date}'"
                )

        if hero_freshness_line is None:
            freshness_errors.append("index.html is missing hero freshness line prefixed with 'Latest:'")
        else:
            if expected_week_label and expected_week_label not in hero_freshness_line:
                freshness_errors.append(
                    f"index.html hero freshness line missing week label '{expected_week_label}'"
                )
            if expected_full_date and expected_full_date not in hero_freshness_line:
                freshness_errors.append(
                    f"index.html hero freshness line missing date '{expected_full_date}'"
                )

    print(f"Audited HTML files: {len(files)}")
    print(f"Published issues: {len(published_slugs)}")

    if missing_links:
        print("\nMissing internal links:")
        for x in missing_links:
            print(f"- {x}")

    print(f"Archive missing issues: {archive_missing or 'none'}")
    print(f"Feed missing issues: {feed_missing or 'none'}")
    print(f"Archive stale issues: {archive_stale or 'none'}")
    print(f"Feed stale issues: {feed_stale or 'none'}")
    if latest_feed_slug:
        print(f"Expected latest issue slug (feed first item): {latest_feed_slug}")
    else:
        print("Expected latest issue slug (feed first item): none")
    if expected_week_label:
        print(f"Expected latest week label: {expected_week_label}")
    if expected_full_date:
        print(f"Expected latest full date: {expected_full_date}")
    print(f"Index latest-edition link errors: {latest_link_errors or 'none'}")
    print(f"Index latest-edition card errors: {latest_card_errors or 'none'}")
    print(f"Index freshness-line errors: {freshness_errors or 'none'}")

    if (
        missing_links
        or archive_missing
        or feed_missing
        or archive_stale
        or feed_stale
        or latest_link_errors
        or latest_card_errors
        or freshness_errors
    ):
        return 1

    print("Release audit OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
