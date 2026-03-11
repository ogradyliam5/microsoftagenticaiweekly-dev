#!/usr/bin/env python3
import argparse
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-id", required=True)
    args = parser.parse_args()

    slug = f"issue-{args.issue_id}"
    canonical_path = f"/posts/{slug}"
    page = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Moved: Microsoft Agentic AI Weekly</title>
  <meta http-equiv=\"refresh\" content=\"0; url={canonical_path}\" />
  <link rel=\"canonical\" href=\"{canonical_path}\" />
  <meta name=\"robots\" content=\"noindex,follow\" />
  <script>
    window.location.replace({canonical_path!r});
  </script>
</head>
<body>
  <p>This issue moved to <a href=\"{canonical_path}\">{canonical_path}</a>.</p>
</body>
</html>
"""

    out_path = ROOT / "posts" / f"issue-{args.issue_id}.html"
    out_path.write_text(page, encoding="utf-8")
    print(str(out_path))


if __name__ == "__main__":
    main()
