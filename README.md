# Microsoft Agentic AI Weekly

A GitHub-friendly static newsletter site for Microsoft Agentic AI professionals.

## What this includes

- Static website (`index.html`, `about.html`, `archive.html`)
- First issue page (`posts/issue-001.html`)
- Newsletter source markdown (`posts/issue-001.md`)
- Lightweight styling (`assets/styles.css`)
- Project plan and publishing workflow (`docs/`)

## Run locally

Because this is static HTML/CSS, you can open `index.html` directly or run a local server:

```bash
python3 -m http.server 8080
# then open http://localhost:8080/microsoftagenticaiweekly/
```

## Suggested GitHub setup

1. Create a repo (e.g. `microsoftagenticaiweekly`)
2. Push this folder to the repo root
3. Enable GitHub Pages from `main` branch root
4. (Optional) connect custom domain (`microsoftagenticaiweekly.com`)

## Publishing workflow

1. Duplicate `docs/ISSUE_TEMPLATE.md`
2. Curate weekly links (target 60% independent / 40% official)
3. Publish markdown + html issue page
4. Add issue to `archive.html`

## Email automation (Buttondown)

A simple API helper is included at `scripts/buttondown.py`.

```bash
python3 scripts/buttondown.py list --status draft
python3 scripts/buttondown.py create --subject "Microsoft Agentic AI Weekly #002" --body-file docs/EMAIL_DRAFT_ISSUE_002.txt
```

Setup + operating notes: `docs/BUTTONDOWN_AUTOMATION.md`

## License

Personal project; add a license file when ready.
