# Weekly pipeline runbook

## What runs each week

1. `scripts/pipeline/build_queue.py`
   - Reads `data/sources.json`
   - Fetches RSS/Atom sources
   - Normalizes basic metadata
   - Applies relevance scoring tuned for agentic AI/Copilot/Foundry/automation/governance topics
   - Down-ranks or excludes low-signal/non-AI posts before queue selection
   - Outputs:
     - `artifacts/editorial_queue-<issue_id>.json`
     - `artifacts/editorial_queue-<issue_id>.md`

2. `scripts/pipeline/validate_queue.py`
   - Enforces minimum quality gates:
     - title/canonical URL/published date required
     - summary bullet length caps
     - evidence snippet cap (<=25 words)

3. `scripts/pipeline/generate_issue.py`
   - Converts queue into one main weekly digest + email draft
   - Adds full human-readable publication date in the issue header
   - Enforces a single placement per item (no repeated items across sections)
   - Uses exactly 4 sections: Power Platform, M365, Microsoft Foundry, Everything else
   - Outputs:
     - `posts/issue-<issue_id>.md`
     - `drafts/email-<issue_id>.md`

4. `scripts/pipeline/run_report.py`
   - Generates a concise run analytics snapshot for the issue
   - Outputs:
     - `artifacts/run_report-<issue_id>.md`

5. `scripts/pipeline/source_candidate_audit.py`
   - Re-checks candidate + rejected feed health for source governance parity
   - Outputs:
     - `artifacts/source_candidate_audit.json`
     - `artifacts/source_candidate_audit.md`
   - Non-blocking in `run_weekly.py` (status is recorded in `artifacts/last_run.json`)

6. `scripts/pipeline/run_weekly.py` summary integrity checks
   - Verifies expected weekly output artifacts exist before writing `artifacts/last_run.json`
   - Fails the run when required artifacts are missing (fail-fast by default)
   - Records:
     - `artifact_check` (`ok` or `missing_artifacts`)
     - `missing_artifacts` array
     - `artifact_checks` map (path -> true/false)
     - `enforce_artifacts` (whether fail-fast mode was enabled)

7. `scripts/pipeline/buttondown_draft.py`
   - Creates a Buttondown **draft** (never sends)
   - Records idempotency metadata:
     - `artifacts/buttondown_drafts.json`

## Approval gates (non-negotiable)

- Publishing website post: Liam approval required.
- Sending email: Liam approval required.
- Adding/removing tracked sources: Liam approval required.

## Local/manual run

```bash
python3 scripts/pipeline/run_weekly.py
```

`--issue-id` format guardrail:
- Must be `YYYY-WW` (ISO week), e.g. `2026-10`
- Week must exist for the target year (`01..52` or `01..53` depending on ISO calendar)

Optional flags:

```bash
# Backfill or regenerate a specific issue id
python3 scripts/pipeline/run_weekly.py --issue-id 2026-10

# Generate queue/site/email artifacts without calling Buttondown API
python3 scripts/pipeline/run_weekly.py --skip-buttondown

# Skip candidate feed-health audit (if running fully offline)
python3 scripts/pipeline/run_weekly.py --skip-source-audit

# Optional: keep writing summary but do not fail the command on missing artifacts
python3 scripts/pipeline/run_weekly.py --no-enforce-artifacts
```

## Sample dry run (Issue 000)

```bash
python3 scripts/pipeline/make_sample_issue000.py
```

## GitHub Actions

Workflow: `.github/workflows/weekly-editorial.yml`

- Scheduled weekly every Monday morning (08:00 Europe/London) + manual dispatch.
- Schedule runs are gated to Monday 08:00 Europe/London; manual `workflow_dispatch` bypasses the time gate.
- Manual dispatch supports optional parity inputs that map directly to `run_weekly.py` flags:
  - `issue_id` -> `--issue-id`
  - `skip_buttondown` -> `--skip-buttondown`
  - `skip_source_audit` -> `--skip-source-audit`
  - `no_enforce_artifacts` -> `--no-enforce-artifacts`
- Manual dispatch validates `issue_id` via shared `scripts/pipeline/issue_id_guard.py` logic, enforcing real ISO-week bounds for the target year before pipeline execution.
- Workflow run also executes `scripts/pipeline/test_issue_id_guard.py` before argument build, so issue-id guardrail regressions fail fast in CI.
- Uses repo secret: `BUTTONDOWN_API_KEY`.
- Opens PR for approval before any publish/send steps.

Local parity command for guardrail regression checks:

```bash
python3 scripts/pipeline/test_issue_id_guard.py
```
