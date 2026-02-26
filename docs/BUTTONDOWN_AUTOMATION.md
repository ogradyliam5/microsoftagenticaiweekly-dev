# Buttondown Automation (Microsoft Agentic AI Weekly)

This project now includes a lightweight API workflow so OpenClaw can operate your newsletter with minimal manual steps.

## Prereqs

Set env vars in OpenClaw config (`~/.openclaw/openclaw.json`):

- `BUTTONDOWN_API_KEY`
- `BUTTONDOWN_REPLY_TO`
- `BUTTONDOWN_FROM_NAME`

## Commands

From repo root:

```bash
python3 scripts/buttondown.py list --status draft
python3 scripts/buttondown.py create \
  --subject "Microsoft Agentic AI Weekly #002" \
  --body-file docs/EMAIL_DRAFT_ISSUE_002.txt \
  --description "Weekly curation for Microsoft Agentic AI builders"
python3 scripts/buttondown.py get <email_id>
```

## Operating model

1. Draft issue content in `posts/issue-XXX.md` and/or `docs/EMAIL_DRAFT_ISSUE_XXX.txt`
2. Create Buttondown draft via API (`scripts/buttondown.py create`)
3. Review in Buttondown UI
4. Send/schedule from Buttondown UI (safest)
5. Publish matching issue page in this repo and push to GitHub Pages

## Why this setup

- High automation via API for draft creation/retrieval
- Keeps final send decision in UI for safety/compliance checks
- Works cleanly with your existing GitHub Pages archive
