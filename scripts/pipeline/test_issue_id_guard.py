#!/usr/bin/env python3
"""Regression checks for shared issue-id validation helpers."""

from __future__ import annotations

import datetime as dt
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/pipeline"))

from issue_id_guard import issue_id_max_week, validate_issue_id


def expect_valid(issue_id: str) -> None:
    validate_issue_id(issue_id)


def expect_invalid(issue_id: str, contains: str) -> None:
    try:
        validate_issue_id(issue_id)
    except ValueError as exc:
        msg = str(exc)
        if contains not in msg:
            raise SystemExit(f"Expected '{contains}' in '{msg}'") from exc
        return
    raise SystemExit(f"Expected invalid issue id to fail: {issue_id}")


def main() -> None:
    # Accepts empty issue-id (pipeline defaults to current ISO week).
    expect_valid(None)

    # Shape and bounds checks.
    expect_valid("2026-01")
    expect_invalid("2026-00", "Week must be between")
    expect_invalid("2026-54", "Week must be between")
    expect_invalid("26-01", "Expected format YYYY-WW")

    # Validate dynamic year-specific upper bound behavior.
    for year in (2020, 2021, 2026, 2032):
        max_week = issue_id_max_week(year)
        expect_valid(f"{year}-{max_week:02d}")
        expect_invalid(f"{year}-{max_week + 1:02d}", f"for {year}")

    # Sanity check against Python ISO calendar behavior.
    current_year = dt.datetime.now(dt.timezone.utc).year
    for year in range(current_year - 1, current_year + 2):
        assert issue_id_max_week(year) == dt.date(year, 12, 28).isocalendar().week

    print("issue_id_guard regression tests: PASS")


if __name__ == "__main__":
    main()
