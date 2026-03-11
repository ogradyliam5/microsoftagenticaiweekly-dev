# Buttondown Automation - v2

## Purpose
Create or update Buttondown drafts from generated issue content.

This integration is draft-only. Sending remains manual and approval-gated.

## Required environment variables
- `BUTTONDOWN_API_KEY`
- `BUTTONDOWN_REPLY_TO` (optional but recommended)
- `BUTTONDOWN_FROM_NAME` (optional)
- `BUTTONDOWN_API_BASE_URL` (optional, defaults to `https://api.buttondown.email/v1`; used for local/mock verification)
- `BUTTONDOWN_DRAFT_STATE_PATH` (optional, overrides `artifacts/buttondown_drafts.json`)

## Core commands
List drafts:
```bash
python3 scripts/buttondown.py list --status draft
```

Create draft directly:
```bash
python3 scripts/buttondown.py create --subject "Microsoft Agentic AI Weekly - Issue 2026-10" --body-file drafts/email-2026-10.md
```

Pipeline-driven draft creation:
```bash
python3 scripts/pipeline/run_weekly.py
```

## Idempotency requirements
- Draft creation/update metadata must be persisted (for reruns).
- Re-running the same issue should update or create predictably without duplicate send actions.

Verification:
```bash
python -m unittest tests.pipeline.test_buttondown_draft_unit
```

## Approval-first workflow
1. Generate issue + email draft.
2. Create/update Buttondown draft.
3. Review draft in Buttondown UI.
4. Approve site publish.
5. Approve manual send in Buttondown UI.

No autonomous send is allowed.
