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

## Stage completion log (current cycle)
- [x] Stage 14 complete — see `docs/STAGE14_AUTOMATED_RELEASE_AUDIT_SCRIPT.md` (latest develop commit)
- [x] Stage 15 complete — see `docs/STAGE15_CI_RELEASE_AUDIT_GUARDRAIL.md` (latest develop commit)
- [x] Stage 16 complete — see `docs/STAGE16_PIPELINE_EXECUTION_MODES.md` (latest develop commit)
