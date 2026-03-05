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
   - Classifies feed machine-ingestability (`root_tag` + entry count), so candidate/reject triage highlights parseable-but-non-ingestable endpoints.
   - Records per-feed `ingestability_reason` (`machine_ingestable`, `no_items`, `unsupported_root_tag`, `fetch_failed`) and summary counters for faster reject/candidate cleanup decisions.
  - Includes reason-count breakdown maps for both candidate-add and candidate-reject cohorts (`candidate_add_reason_counts`, `candidate_reject_reason_counts`) so triage can quickly separate machine-ingestable opportunities from endpoint failures.
  - Adds reason-percentage maps (`candidate_add_reason_percentages`, `candidate_reject_reason_percentages`) for at-a-glance cohort weighting during approval review.
  - Adds dominant ingestability reason fields and candidate-vs-reject percentage deltas (`candidate_add_top_ingestability_reason`, `candidate_reject_top_ingestability_reason`, `candidate_add_vs_reject_reason_percentage_delta`) for faster triage direction.
  - Emits actionable candidate ID queues (`candidate_add_promotion_candidate_ids`, `candidate_add_failed_ids`, `candidate_add_non_ingestable_ids`, `candidate_reject_revival_candidate_ids`, `candidate_reject_still_blocked_ids`, `candidate_reject_non_ingestable_ids`) for approval/rejection follow-through.
  - Adds reason-bucketed non-ingestable queues (`candidate_add_non_ingestable_ids_by_reason`, `candidate_reject_non_ingestable_ids_by_reason`) and sorts all queue IDs deterministically for stable operator diffs.
  - Adds non-ingestable priority queues (`candidate_add_non_ingestable_priority_ids`, `candidate_reject_non_ingestable_priority_ids`) ordered by operator urgency: `fetch_failed`, `no_items`, `unsupported_root_tag`, `unknown`.
  - Adds a deterministic promotion opportunity queue (`promotion_opportunity_ids`) ranked by source cohort (`candidate_add` before `candidate_reject`) and item volume, plus cohort counts/percentages and ranked metadata (`promotion_opportunity_breakdown`, `promotion_opportunity_cohort_percentages`, `promotion_opportunity_rows`, `promotion_opportunity_top_ids`).
   - Outputs:
     - `artifacts/source_candidate_audit.json`
     - `artifacts/source_candidate_audit.md`
   - Non-blocking in `run_weekly.py` (status is recorded in `artifacts/last_run.json`)

6. `scripts/pipeline/run_weekly.py` summary integrity checks
   - Verifies expected weekly output artifacts exist before writing `artifacts/last_run.json`
   - Renders a human-readable run summary to `artifacts/last_run.md`
   - Persists timestamped run-history snapshots to `artifacts/run_history/` with bounded retention (latest 30 runs)
   - Uses collision-safe snapshot naming (`-01`, `-02`, … suffix) when multiple runs finish in the same second
   - Keeps `artifacts/last_run.json` and `artifacts/last_run.md` as canonical latest pointers
   - Fails the run when required artifacts are missing (fail-fast by default)
   - Captures step-level execution diagnostics when core pipeline steps fail
   - Adds timing telemetry for run-level and per-step runtime evidence
   - Records:
     - `pipeline_status` (`ok` or `failed`)
     - `failed_step` object (`name`, `command`, `exit_code`) when applicable
     - `step_results` array for successful/failed/skipped steps, including `started_at`, `finished_at`, `duration_seconds`
     - `run_started_at`, `run_finished_at`, `run_duration_seconds`
     - `artifact_check` (`ok` or `missing_artifacts`)
     - `missing_artifacts` array
     - `artifact_checks` map (required path -> true/false)
     - `output_artifacts` map (named output label -> canonical path)
     - `output_artifact_checks` map (named output label -> `{path, exists}`)
     - `enforce_artifacts` (whether fail-fast mode was enabled)
     - `run_history` object (snapshot paths + run-history index paths + retention metadata for timestamped history copies, including retained run count, JSON/markdown retained counts, and orphan snapshot counts)

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
- Workflow validates `artifacts/last_run.json` contract with `scripts/pipeline/validate_last_run_summary.py` before publishing CI summary output, including step-result timing contract checks (UTC timestamps + non-negative durations), duration numerical parity checks (`run_duration_seconds` and per-step `duration_seconds` must align with timestamp deltas within tolerance), run-level step timeline envelope + sequencing checks (step timestamps must stay within `run_started_at`/`run_finished_at` bounds and remain non-decreasing across execution order), and run-history index parity (`index.json`/`index.md` presence, retained-count consistency, descending mtime ordering, snapshot file existence checks, latest-index entry alignment with `run_history.json` / `run_history.markdown`, timestamp/path consistency checks for index entries, and JSON/markdown latest snapshot filename timestamp+suffix parity checks).
- Uses repo secret: `BUTTONDOWN_API_KEY`.
- Uploads generated artifacts even when pipeline execution fails (for failure forensics in Actions UI).
- Publishes `artifacts/last_run.md` into the Actions job summary (falls back to JSON if markdown is unavailable).
- Opens PR for approval before any publish/send steps.

Local parity commands for guardrail regression checks:

```bash
python3 scripts/pipeline/test_issue_id_guard.py
python3 scripts/pipeline/validate_last_run_summary.py
```
