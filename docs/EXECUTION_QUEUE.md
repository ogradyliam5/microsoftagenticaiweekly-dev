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
