# Execution Queue (PM-controlled)

Purpose: prevent stop/start drift and force delivery through ordered stages.

## Rules
- Work in strict stage order.
- No stage is considered complete without:
  1) commit hash,
  2) file list,
  3) dev preview sync confirmation.
- Progress updates must include tangible outputs only.
- If interrupted by chat/system events, resume current stage immediately.
- Never idle between stages: immediately dispatch next stage/subagent unless a hard blocker exists.
- Overnight mode: continue autonomous execution without waiting for user pings; send milestone updates with proof only.
- PM cadence: checkpoint updates are outcome-based (not time-based) and must include next concrete step already in progress.

## Stage Plan

### Stage 1 — Source Engine Stabilization
- Promote approved practitioner candidates into tracked sources.
- Validate feed health and mark hard failures.
- Regenerate queue + draft artifacts.

### Stage 2 — Content Quality Pass
- Improve issue copy quality for Jan/Feb issues (#001-#008):
  - clearer "why it matters"
  - role-targeting (Builder/Platform Owner/Leader)
  - action signal labels.

### Stage 3 — Frontend Redesign Iteration 2
- Replace homepage and archive framing with cleaner cross-stack messaging.
- Keep provenance and approval-first cues.

### Stage 4 — Final QA + Release Readiness
- Link checks, metadata consistency, feed correctness, schedule notes.
- Publish final dev sync and handoff checklist.

## Stage Plan (next cycle)

### Stage 5 — Content Personality Upgrade
- Rewrite homepage hero + section intros in the approved human/quirky brief voice.
- Replace rigid labels with natural phrasing and short punchy summaries.
- Keep trust/provenance cues but reduce corporate tone.

### Stage 6 — Weekly Issue Format Upgrade
- Refactor issue pages to preferred format:
  - short narrative line per item ("Microsoft updated...", "X published...")
  - easier scanning and better engagement
  - drop rigid moat-style/over-structured blocks
- Apply to latest issue and template for future issues.

### Stage 7 — Source Mix Tuning
- Increase individual-practitioner ratio in weekly outputs.
- Reduce low-signal/noisy entries.
- Add lightweight freshness + quality scoring notes in generated queue report.

### Stage 8 — Final Polish + Production Promotion Plan
- Final readability QA pass on dev.
- Produce merge checklist and promote-ready handoff.

## Stage completion log

- [x] Stage 1 complete — `ee0d109`
- [x] Stage 2 complete — `a4b2627`
- [x] Stage 3 complete — `e2c7c5f`
- [x] Stage 4 complete — see `docs/STAGE4_QA_RELEASE_READINESS.md`
- [x] Stage 5 complete — `9816f96`
- [x] Stage 6 complete — `94b2b63`
- [x] Stage 7 complete — source mix tuning + freshness/quality scoring notes added (see latest develop commit)
- [x] Stage 8 complete — see `docs/STAGE8_FINAL_POLISH_PRODUCTION_PLAN.md`

## Stage Plan (next cycle)

### Stage 9 — Buttondown Reliability Hardening
- Diagnose and fix HTTP 422 in `scripts/pipeline/buttondown_draft.py`.
- Ensure idempotent create/update behavior for weekly draft IDs.
- Add clear error handling + actionable logs without blocking site artifact generation.

### Stage 10 — Interesting-Only Source Ranking
- Tune scoring to prioritize updates, guides, how-tos, demos, and real build reports.
- Down-rank generic marketing/news-noise items.
- Add explicit content-type weighting in queue output.

### Stage 11 — Homepage Voice v3
- Rewrite homepage in human, engaging style per Liam’s preferences.
- Keep concise trust cues; reduce framework-heavy language.

### Stage 12 — Weekly Renderer v2 Everywhere
- Apply narrative item format to all active issue templates and latest drafts.
- Keep scannable, short summaries with source links.

### Stage 13 — Production Promotion Readiness
- Final QA pass + release checklist + rollback notes.
- Prepare `develop -> main` promotion handoff.

## Stage completion log (next cycle)
- [x] Stage 9 complete — see `docs/STAGE9_BUTTONDOWN_RELIABILITY_HARDENING.md` (latest develop commit)
- [x] Stage 10 complete — see `docs/STAGE10_INTERESTING_ONLY_SOURCE_RANKING.md` (latest develop commit)
- [x] Stage 11 complete — see `docs/STAGE11_HOMEPAGE_VOICE_V3.md` (latest develop commit)
- [x] Stage 12 complete — see `docs/STAGE12_WEEKLY_RENDERER_V2_EVERYWHERE.md` (latest develop commit)
- [x] Stage 13 complete — see `docs/STAGE13_PRODUCTION_PROMOTION_READINESS.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 14 — Automated Release Audit Script
- Convert final QA checks into a single reusable script.
- Validate internal links, archive coverage, and RSS coverage in one command.
- Document evidence so promotion checks are repeatable.

### Stage 15 — CI Release Audit Guardrail
- Add a GitHub Actions workflow that runs the release audit script on PRs/pushes.
- Ensure failures block regressions before `develop -> main` promotion.
- Document the CI guardrail and local parity command.

### Stage 16 — Pipeline Execution Modes (Backfill + Safe Local Run)
- Add explicit run mode flags to weekly pipeline for deterministic backfills.
- Allow local artifact generation without requiring Buttondown API calls.
- Record Buttondown execution status in run summary output.

### Stage 17 — Weekly Run Analytics Report
- Generate a reusable run report markdown artifact per issue.
- Include output mix breakdown (product area/source bucket/content type) + top scored items.
- Wire report generation into weekly pipeline so every run emits the analytics snapshot.

## Stage completion log (current cycle)
- [x] Stage 14 complete — see `docs/STAGE14_AUTOMATED_RELEASE_AUDIT_SCRIPT.md` (latest develop commit)
- [x] Stage 15 complete — see `docs/STAGE15_CI_RELEASE_AUDIT_GUARDRAIL.md` (latest develop commit)
- [x] Stage 16 complete — see `docs/STAGE16_PIPELINE_EXECUTION_MODES.md` (latest develop commit)
- [x] Stage 17 complete — see `docs/STAGE17_WEEKLY_RUN_ANALYTICS_REPORT.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 24 — Homepage Visual Polish + Issue Card UX
- Improve homepage card hierarchy, typography rhythm, and spacing for faster scan.
- Add consistent metadata on issue cards (full date + 1-line teaser) and tighten CTA clarity.
- Ensure cover images render crisply across breakpoints and dark/light contexts.

### Stage 25 — Edition Data Consistency Pass
- Verify all edition cards map to valid issue pages and matching feed/archive entries.
- Regenerate any missing issue cover or teaser data from latest artifacts.

## Stage completion log (next cycle)
- [x] Stage 24 complete — see `docs/STAGE24_HOMEPAGE_VISUAL_POLISH_ISSUE_CARD_UX.md` (latest develop commit)
- [x] Stage 25 complete — see `docs/STAGE25_EDITION_DATA_CONSISTENCY_PASS.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 18 — Weekly Digest Structure + Relevance Correction
- Enforce one-pass digest structure with only 4 sections: Power Platform, M365, Microsoft Foundry, Everything else.
- Ensure each item appears once only (global dedupe across sections).
- Add full human-readable publication date in issue header.
- Remove disliked labels/phrases (Adopt/Pilot/Watch, best-fit, what-to-do-next, keep-an-eye-on).
- Ensure creator names are used directly in item lines.
- Tighten relevance filter to reduce non-AI content in latest issue.

## Stage completion log (next cycle)
- [x] Stage 18 complete — see `docs/STAGE18_WEEKLY_DIGEST_STRUCTURE_RELEVANCE_CORRECTION.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 19 — Legacy Issue Format Backfill
- Regenerate older issue artifacts that still used deprecated Adopt/Pilot/Watch framing.
- Align markdown + HTML issue pages to the current 4-section digest renderer.
- Ensure archived issue outputs match latest narrative style and publication metadata format.

## Stage completion log (current cycle)
- [x] Stage 19 complete — legacy issue artifacts regenerated for `000` and `2026-09` (latest develop commit)

## Stage Plan (next cycle)

### Stage 20 — Release Audit Coverage Repair (Legacy Issue 000)
- Fix release audit failures caused by `issue-000` missing from archive and RSS coverage.
- Re-run automated release audit and verify zero archive/feed coverage gaps.
- Record evidence and keep audit parity for future `develop -> main` promotion checks.

## Stage completion log (next cycle)
- [x] Stage 20 complete — archive + RSS coverage repaired for `issue-000`; release audit passes (latest develop commit)

## Stage Plan (current cycle)

### Stage 21 — Bidirectional Release Audit Coverage Guardrail
- Extend release audit checks to detect stale issue references in archive/feed (items that no longer exist in `posts/`).
- Keep fail-fast behavior for both missing and stale issue coverage so promotion checks catch drift in both directions.
- Record verification evidence and local parity command.

## Stage completion log (current cycle)
- [x] Stage 21 complete — stale archive/feed reference checks added to release audit (latest develop commit)

## Stage Plan (next cycle)

### Stage 26 — Practitioner Source Candidate Hygiene Refresh
- Refresh discovery candidates with active, parseable practitioner RSS feeds aligned to Copilot Studio/Power Platform operations.
- Deduplicate source candidates against existing core sources and normalize reject reasons for blocked/noisy feeds.
- Update shortlist documentation with approval-ready rationale while keeping core `sources[]` unchanged.

## Stage completion log (next cycle)
- [x] Stage 26 complete — practitioner candidate refresh documented; `data/sources.json` + `docs/SOURCE_SHORTLIST.md` updated (latest develop commit)

## Stage Plan (current cycle)

### Stage 27 — Candidate Feed Health Audit Automation
- Add a reusable script to re-check discovery candidate and rejected feed endpoint health in one run.
- Emit JSON + markdown evidence artifacts for approval discussions.
- Document local parity command and findings so promotions/rejections are backed by fresh feed-health data.

## Stage completion log (current cycle)
- [x] Stage 27 complete — candidate/reject feed audit script + artifacts added; see `docs/STAGE27_CANDIDATE_FEED_HEALTH_AUDIT_AUTOMATION.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 28 — Weekly Pipeline Governance Parity Hook
- Run candidate/rejected feed audit automatically during weekly pipeline runs (non-blocking).
- Record source-audit execution status in `artifacts/last_run.json` for traceable run summaries.
- Document local parity and offline skip flag so deterministic backfills remain practical.

## Stage completion log (next cycle)
- [x] Stage 28 complete — weekly pipeline now executes candidate feed audit with status reporting; see `docs/STAGE28_WEEKLY_PIPELINE_GOVERNANCE_PARITY_HOOK.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 29 — Weekly Output Artifact Integrity Guardrail
- Add an artifact existence verification step in `run_weekly.py` before final run summary write.
- Record missing artifact paths in `artifacts/last_run.json` for fail-fast operator visibility.
- Document local parity and evidence in a dedicated stage note.

## Stage completion log (current cycle)
- [x] Stage 29 complete — run summary now includes artifact integrity checks; see `docs/STAGE29_WEEKLY_OUTPUT_ARTIFACT_INTEGRITY_GUARDRAIL.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 30 — Weekly Artifact Enforcement Fail-Fast
- Enforce non-zero exit in `run_weekly.py` when required weekly artifacts are missing.
- Keep explicit opt-out flag for local diagnostics (`--no-enforce-artifacts`).
- Document parity command and evidence so CI/local behavior stays aligned.

## Stage completion log (next cycle)
- [x] Stage 30 complete — fail-fast artifact enforcement added to weekly pipeline; see `docs/STAGE30_WEEKLY_ARTIFACT_ENFORCEMENT_FAIL_FAST.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 31 — Weekly Workflow Manual-Dispatch Reliability
- Ensure `.github/workflows/weekly-editorial.yml` runs pipeline on `workflow_dispatch` regardless of Monday 08:00 London gate.
- Keep schedule gating intact for cron-triggered runs.
- Document parity behavior in `docs/WEEKLY_PIPELINE.md`.

## Stage completion log (current cycle)
- [x] Stage 31 complete — manual dispatch now bypasses schedule gate while cron remains Monday-08:00 guarded (latest develop commit)

## Stage Plan (next cycle)

### Stage 32 — Workflow Dispatch Input Parity
- Add explicit `workflow_dispatch` inputs for issue override and safe-run flags.
- Map dispatch inputs directly to `scripts/pipeline/run_weekly.py` arguments.
- Document parity behavior in `docs/WEEKLY_PIPELINE.md` for operator clarity.

## Stage completion log (next cycle)
- [x] Stage 32 complete — workflow_dispatch inputs now map to weekly pipeline args; see `docs/STAGE32_WORKFLOW_DISPATCH_INPUT_PARITY.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 33 — Issue ID Input Validation Guardrail
- Add strict ISO week issue-id validation in `scripts/pipeline/run_weekly.py` so invalid backfill IDs fail fast.
- Add manual dispatch input format guard in `.github/workflows/weekly-editorial.yml` for early operator feedback.
- Document issue-id validation expectations in `docs/WEEKLY_PIPELINE.md`.

### Stage 34 — Workflow ISO Week Validation Parity
- Upgrade `workflow_dispatch` `issue_id` validation from shape-only (`YYYY-WW`) to real ISO-week bounds by year.
- Fail fast in workflow argument build step with explicit operator-facing errors for out-of-range weeks.
- Document parity behavior in `docs/WEEKLY_PIPELINE.md`.

### Stage 35 — Shared Issue-ID Validation Parity
- Remove duplicate issue-id guard logic across local and workflow paths.
- Use a single validation module for CLI + manual dispatch parity.
- Document shared-validator behavior and verification evidence.

## Stage completion log (current cycle)
- [x] Stage 33 complete — ISO week issue-id validation guardrail added for CLI + workflow dispatch; see `docs/STAGE33_ISSUE_ID_INPUT_VALIDATION_GUARDRAIL.md` (latest develop commit)
- [x] Stage 34 complete — workflow dispatch now validates real ISO-week bounds; see `docs/STAGE34_WORKFLOW_ISO_WEEK_VALIDATION_PARITY.md` (latest develop commit)
- [x] Stage 35 complete — shared issue-id validator used by CLI + workflow dispatch; see `docs/STAGE35_SHARED_ISSUE_ID_VALIDATION_PARITY.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 36 — Issue-ID Validation Regression Coverage
- Add a deterministic regression test script for shared `issue_id_guard` logic.
- Execute guardrail regression checks in weekly workflow before pipeline arg build.
- Document local parity command and verification evidence.

## Stage completion log (next cycle)
- [x] Stage 36 complete — issue-id guard regression checks added to CI + local parity docs; see `docs/STAGE36_ISSUE_ID_VALIDATION_REGRESSION_COVERAGE.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 37 — Workflow Failure Artifact Retention Parity
- Ensure weekly workflow uploads generated artifacts even when pipeline execution fails.
- Keep artifact upload non-blocking (`warn`) when files are absent so diagnostics remain visible.
- Document CI behavior in the weekly runbook for operator parity.

## Stage completion log (current cycle)
- [x] Stage 37 complete — weekly workflow now uploads artifacts on failure paths; see `docs/STAGE37_WORKFLOW_FAILURE_ARTIFACT_RETENTION_PARITY.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 38 — Weekly Pipeline Failure Diagnostics Parity
- Ensure `run_weekly.py` records step-level failure diagnostics in `artifacts/last_run.json` when core pipeline commands fail.
- Preserve artifact integrity checks in the same summary so CI/local troubleshooting stays deterministic.
- Document local parity verification and expected failure evidence paths.

## Stage completion log (next cycle)
- [x] Stage 38 complete — run summary now includes pipeline status + failed-step diagnostics; see `docs/STAGE38_WEEKLY_PIPELINE_FAILURE_DIAGNOSTICS_PARITY.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 39 — Weekly Pipeline Runtime Telemetry Parity
- Add run-level timing telemetry (`run_started_at`, `run_finished_at`, `run_duration_seconds`) in `artifacts/last_run.json`.
- Add per-step timing metadata (`started_at`, `finished_at`, `duration_seconds`) for core and optional pipeline steps.
- Document runtime telemetry fields in `docs/WEEKLY_PIPELINE.md` for CI/local troubleshooting parity.

### Stage 40 — Run Summary Readability + CI Surface Parity
- Generate `artifacts/last_run.md` from `artifacts/last_run.json` on every weekly run.
- Publish run summary markdown to GitHub Actions job summary for faster operator triage.
- Document summary artifact + CI behavior in runbook and PR quick links.

## Stage completion log (current cycle)
- [x] Stage 39 complete — runtime telemetry added to weekly run summary; see `docs/STAGE39_WEEKLY_PIPELINE_RUNTIME_TELEMETRY_PARITY.md` (latest develop commit)
- [x] Stage 40 complete — markdown run summary artifact + Actions job summary publishing added; see `docs/STAGE40_RUN_SUMMARY_READABILITY_CI_SURFACE_PARITY.md` (latest develop commit)
- [x] Stage 41 complete — theme bootstrap hardening + asset cache versioning shipped (commit `b50025b`)

## Stage Plan (next cycle)

### Stage 42 — Practitioner Candidate Freshness + Reject Reason Normalization
- Refresh practitioner discovery candidate set with current high-signal Copilot Studio/Power Platform voices.
- Normalize rejected-feed reasons when endpoint health changes (blocked -> reachable) while preserving approval-first policy.
- Re-run candidate feed audit artifacts so shortlist decisions have current evidence.

## Stage completion log (next cycle)
- [x] Stage 42 complete — candidate freshness refresh + reject reason normalization with refreshed audit artifacts (latest develop commit)

## Stage Plan (current cycle)

### Stage 43 — Run Output Artifact Traceability Parity
- Add named output artifact mapping to weekly run summary JSON so operators can inspect canonical paths quickly.
- Include per-artifact existence status in markdown run summary for CI/local triage parity.
- Document verification evidence and parity command in a dedicated stage note.

## Stage completion log (current cycle)
- [x] Stage 43 complete — output artifact traceability added to run summaries; see `docs/STAGE43_RUN_OUTPUT_ARTIFACT_TRACEABILITY_PARITY.md` (latest develop commit)
- [x] Stage 44 complete — run summary contract validator + CI guardrail added; see `docs/STAGE44_RUN_SUMMARY_CONTRACT_VALIDATION_GUARDRAIL.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 45 — Run Summary History Retention
- Persist per-run timestamped summary snapshots alongside `artifacts/last_run.json` for longitudinal debugging.
- Keep `last_run.*` as canonical latest pointers while adding bounded retention policy.
- Document local parity command and retention behavior in runbook.

## Stage completion log (next cycle)
- [x] Stage 45 complete — run-summary history snapshots + bounded retention shipped; see `docs/STAGE45_RUN_SUMMARY_HISTORY_RETENTION.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 46 — Run History Collision-Proof Snapshots
- Prevent same-second run-history snapshot name collisions from overwriting prior evidence.
- Keep deterministic suffixing when duplicate timestamped names are detected.
- Extend summary contract/docs with retained markdown snapshot count for parity.

## Stage completion log (current cycle)
- [x] Stage 46 complete — collision-safe run-history snapshot naming + run-history metadata parity shipped; see `docs/STAGE46_RUN_HISTORY_COLLISION_PROOF_SNAPSHOTS.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 47 — Run-History Pair Retention Parity
- Retain bounded run-history snapshots by run pair (JSON + markdown) instead of per-file count.
- Prevent retention trimming from halving effective run history capacity.
- Extend summary contract/markdown/docs with retained run count and orphan snapshot diagnostics.

## Stage completion log (next cycle)
- [x] Stage 47 complete — run-history retention now trims by run snapshot pair with parity diagnostics; see `docs/STAGE47_RUN_HISTORY_PAIR_RETENTION_PARITY.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 48 — Run-History Index Parity
- Generate canonical run-history index artifacts (`index.json` + `index.md`) during weekly runs.
- Surface index paths in `artifacts/last_run.json` and markdown run summary output.
- Extend summary contract/docs so CI + local verification enforce index parity.

## Stage completion log (current cycle)
- [x] Stage 48 complete — run-history index artifacts + summary/validator parity shipped; see `docs/STAGE48_RUN_HISTORY_INDEX_PARITY.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 49 — Run-History Index Contract Guardrail
- Validate run-history index artifact presence + metadata consistency from `validate_last_run_summary.py`.
- Ensure latest run snapshot paths recorded in `run_history` are represented in the retained run-history index.
- Document parity command and expected failure evidence.

## Stage completion log (next cycle)
- [x] Stage 49 complete — run-history index contract guardrail added to summary validator; see `docs/STAGE49_RUN_HISTORY_INDEX_CONTRACT_GUARDRAIL.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 50 — Run-History Index Ordering Guardrail
- Enforce deterministic descending chronology checks for run-history index entries.
- Validate indexed snapshot paths exist on disk (JSON/markdown) so index drift fails fast.
- Add human-readable snapshot mtime fields and document parity behavior.

## Stage completion log (current cycle)
- [x] Stage 50 complete — run-history index ordering + on-disk snapshot parity checks added; see `docs/STAGE50_RUN_HISTORY_INDEX_ORDERING_GUARDRAIL.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 51 — Run-History Latest Snapshot Alignment Guardrail
- Extend run-summary contract validation to require that run-history index latest entry matches `run_history.json` and `run_history.markdown` from the current run.
- Keep fail-fast behavior when index ordering or pointer metadata drifts.
- Document local parity command + verification evidence in a dedicated stage note.

## Stage completion log (next cycle)
- [x] Stage 51 complete — latest run-history snapshot alignment guardrail added to validator; see `docs/STAGE51_RUN_HISTORY_LATEST_SNAPSHOT_ALIGNMENT_GUARDRAIL.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 52 — Run-History Index Timestamp + Path Consistency Guardrail
- Extend run-summary validator to enforce strict UTC timestamp parsing across summary + run-history index fields.
- Require `mtime_iso` and numeric `mtime` consistency in run-history index entries.
- Fail fast when run-history snapshot path prefixes or json/markdown stem pairing drift.

## Stage completion log (current cycle)
- [x] Stage 52 complete — run-history index timestamp/path consistency guardrail shipped; see `docs/STAGE52_RUN_HISTORY_INDEX_TIMESTAMP_PATH_CONSISTENCY_GUARDRAIL.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 53 — Latest Snapshot Filename Parity Guardrail
- Extend run-summary contract validation to parse latest run-history snapshot filenames for strict `last_run-<issue_id>-<stamp>[-NN]` format.
- Fail fast when `run_history.json` / `run_history.markdown` diverge on issue-id, timestamp, or collision suffix.
- Enforce latest snapshot timestamp is not later than summary `run_finished_at` / `generated_at`; document parity evidence.

## Stage completion log (next cycle)
- [x] Stage 53 complete — latest snapshot filename parity + timestamp bounds guardrail added; see `docs/STAGE53_LATEST_SNAPSHOT_FILENAME_PARITY_GUARDRAIL.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 54 — Step-Result Timing Contract Guardrail
- Extend `validate_last_run_summary.py` to enforce step-result timestamp and duration validity.
- Require UTC timestamp shape + monotonic step timing for non-failed steps.
- Document parity expectations so CI catches malformed diagnostic payloads early.

## Stage completion log (current cycle)
- [x] Stage 54 complete — step-result timing contract validation added; see `docs/STAGE54_STEP_RESULT_TIMING_CONTRACT_GUARDRAIL.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 55 — Duration Numerical Parity Guardrail
- Extend `validate_last_run_summary.py` to enforce run-level duration parity vs timestamp delta.
- Enforce per-step duration parity vs `finished_at - started_at` with tolerance for monotonic-vs-wall-clock drift.
- Document parity behavior and verification evidence in weekly runbook + dedicated stage note.

## Stage completion log (next cycle)
- [x] Stage 55 complete — duration numerical parity guardrail added to summary validator; see `docs/STAGE55_DURATION_NUMERICAL_PARITY_GUARDRAIL.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 56 — Step Timeline Envelope + Sequencing Guardrail
- Extend `validate_last_run_summary.py` to enforce that step timestamps stay within run-level start/finish bounds.
- Enforce non-decreasing step execution order in `step_results` so timeline regressions fail fast.
- Document parity behavior + verification evidence in weekly runbook and dedicated stage note.

## Stage completion log (current cycle)
- [x] Stage 56 complete — run-level step timeline envelope + sequencing guardrail added; see `docs/STAGE56_STEP_TIMELINE_ENVELOPE_SEQUENCING_GUARDRAIL.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 57 — Candidate Intake Feed Eligibility Hardening
- Keep `candidates.add` limited to machine-ingestable RSS/Atom endpoints.
- Move manual-watch/non-feed discovery entries out of candidate automation intake.
- Refresh shortlist and candidate audit artifacts so approval discussions are based on current feed-health evidence.

## Stage completion log (next cycle)
- [x] Stage 57 complete — candidate intake feed eligibility hardened with refreshed shortlist + audit artifacts; see `docs/STAGE57_CANDIDATE_INTAKE_FEED_ELIGIBILITY_HARDENING.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 58 — Candidate Audit Machine-Ingestability Classification
- Extend candidate/rejected source audit output with feed ingestability classification (`root_tag`, parsed item count, machine-ingestable boolean).
- Add summary counters for non-ingestable candidate-add feeds and now-ingestable rejected feeds to speed approval triage.
- Document parity behavior and verification evidence in runbook + dedicated stage note.

## Stage completion log (current cycle)
- [x] Stage 58 complete — candidate audit ingestability classification + summary counters shipped; see `docs/STAGE58_CANDIDATE_AUDIT_MACHINE_INGESTABILITY_CLASSIFICATION.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 59 — Candidate Audit Ingestability Reason Breakdown
- Add per-feed ingestability reason classification to candidate/reject audit output (`machine_ingestable`, `no_items`, `unsupported_root_tag`, `fetch_failed`).
- Add summary counters for non-ingestable reason breakdown to speed source triage decisions.
- Regenerate audit artifacts and document parity behavior in runbook + dedicated stage note.

## Stage completion log (next cycle)
- [x] Stage 59 complete — ingestability reason breakdown + triage counters added to source candidate audit outputs; see `docs/STAGE59_CANDIDATE_AUDIT_INGESTABILITY_REASON_BREAKDOWN.md` (latest develop commit)

## Stage Plan (current cycle)

### Stage 60 — Candidate Audit Reason-Count Parity
- Add cohort-level ingestability reason-count maps for both candidate-add and candidate-reject feeds.
- Surface the new reason-count breakdown in markdown audit output for faster triage.
- Regenerate audit artifacts and document parity evidence in a dedicated stage note.

## Stage completion log (current cycle)
- [x] Stage 60 complete — candidate-add/reject reason-count parity added to source candidate audit outputs; see `docs/STAGE60_CANDIDATE_AUDIT_REASON_COUNT_PARITY.md` (latest develop commit)

## Stage Plan (next cycle)

### Stage 61 — Candidate Audit Reason-Percentage Parity
- Add cohort-level ingestability reason-percentage maps for candidate-add and candidate-reject feeds.
- Surface reason percentages in markdown audit output alongside reason counts.
- Regenerate audit artifacts and document parity evidence in a dedicated stage note.

## Stage completion log (next cycle)
- [x] Stage 61 complete — candidate-add/reject reason-percentage parity added to source candidate audit outputs; see `docs/STAGE61_CANDIDATE_AUDIT_REASON_PERCENTAGE_PARITY.md` (latest develop commit)
