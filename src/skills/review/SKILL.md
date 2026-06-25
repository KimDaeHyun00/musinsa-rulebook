---
name: review
description: >
  Review the current code change (git diff / staged / a PR) against the team's
  cascading rulebook and produce a conformance report with a score. Use when the
  user says "/review", "ship-check", "PR 전 점검", "무신사 규칙으로 검수",
  "리뷰해줘 규칙대로", or right before committing/opening a PR. Loads the seed rules
  shipped with this plugin plus the repo-local .musinsa/rules.yaml.
---

# Musinsa Rulebook — Review

You are reviewing a code change against the team's accumulated rulebook and scoring it.
The point is not generic code review — it is checking conformance to *this team's*
hard-won, written-down rules, and showing exactly where the change breaks them.

## 1. Load the rulebook (cascading, later layers override earlier by `id`)

1. **seed** — `${CODEX_PLUGIN_ROOT}/rules/seed.yaml` (Musinsa public engineering lessons, shipped with this plugin). If `CODEX_PLUGIN_ROOT` is unset, find `rules/seed.yaml` next to this plugin.
2. **org** *(optional)* — if `.musinsa/org-source` exists in the repo, read the rules file it points to. Skip silently if absent.
3. **repo** — `.musinsa/rules.yaml` in the repo root (the team's own rules, grown via the `remember` skill). Skip if absent.

Merge into one effective ruleset: a rule `id` present in a later layer replaces the same `id` in an earlier one. Keep each rule's `source` and `added_by`.

## 2. Determine what to review

- Default: the working change — run `git diff --no-color` (and `git diff --staged --no-color`). If both empty, review `git diff` against the default branch (`git merge-base`).
- If the user named a path or PR, scope to that.
- Collect the list of changed files + the diff hunks.

## 3. Deterministic pass first (hybrid — do NOT skip)

Run the bundled scanner in **report mode** over the changed files. Pass the seed rules first, then the repo rulebook if present (later layers override same-id rules):

```
python3 "${CODEX_PLUGIN_ROOT}/scripts/check.py" --report \
  --rules "${CODEX_PLUGIN_ROOT}/rules/seed.yaml" [--rules .musinsa/rules.yaml] \
  --files <changed files...>
```

This prints the full, reproducible findings block: the score, the gate, and for each pattern-matched violation the `[dimension]`, `file:line`, points, rule title, **근거 (with the original Musinsa metrics), 👉 fix, and 🔗 source URL**. Capture this block exactly — it is the deterministic, auditable core. The score must not drift between runs for the same diff.

If the scanner cannot run (missing dep), say so explicitly and fall back to manual matching — never silently skip.

## 4. Judgment pass (for `detect.llm_hint`)

Some rules can't be caught by regex (e.g. `golden-master-before-refactor`, deeper coupling smells). Read the diff and judge using each rule's `llm_hint`. When you flag one, format it **identically** to a scanner finding (severity, `[dimension]`, `file:line`, 규칙 / 근거 / 👉 / 🔗 using that rule's own rationale/fix/source verbatim) and recompute the score with the same weights below. Only flag when confident with a concrete `file:line`; when unsure use `info`.

Score: start 100; `block` −15, `warn` −8, `info` −2 (cap 100); any `block` ⇒ Gate **BLOCKED**; one finding per (rule_id, file, line).

## 5. Output — 3 parts, in this exact order

A busy engineer must grasp and act on this in seconds. Output:

**(1) 한 줄 판정 요약** — your own words, ≤2 lines. **Lead with the score and gate**, then the count by severity and the single most important thing to fix. Example:
> 🔴 **53/100 · BLOCKED** — 위반 5건(치명적 1: 인덱스 무력화). 상품상세 쿠폰 쿼리가 풀스캔이라 배포 전 필수 수정.

**(2) 검증 결과 (VERBATIM)** — reproduce the `check.py --report` block (plus any judgment-pass findings in the same format), **worst severity first**. Do **NOT** paraphrase, shorten, or drop the 근거 수치 / 🔗 출처 — those are the auditable evidence and the whole point. Reproduce them exactly as the scanner emits.

**(3) 우선순위 수정 플랜** — a short numbered list, blockers first, one line each: `file:line` + the concrete fix. Close with: the Gate opens once every `block` item is resolved. If you spot a recurring issue not yet in the rulebook, suggest capturing it with `/remember`.

If there are zero findings, output only:
> ✅ **Musinsa Readiness 100/100 · PASS** — 룰북 위반 없음.

Never invent a violation to pad the report. Terse, scannable, action-first.
