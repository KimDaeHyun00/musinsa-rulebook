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

Run the bundled scanner over the changed files:

```
python3 "${CODEX_PLUGIN_ROOT}/scripts/check.py" --rules <merged-rules-path-or-seed> --files <changed files...>
```

It returns JSON hits `{rule_id, file, line, snippet}` for every rule whose `detect.patterns` match. These are high-confidence, reproducible findings — the score must not drift between runs for the same diff because of them.

If the scanner cannot run (missing dep), say so explicitly in the report and fall back to manual pattern matching — never silently skip.

## 4. Judgment pass (for `detect.llm_hint`)

For rules whose findings depend on design judgment (e.g. `golden-master-before-refactor`, `type-branch-to-strategy`), read the actual diff and decide using the rule's `llm_hint`. Only flag when you are confident and can point to a specific file:line. When unsure, mark `info`, not `block`.

## 5. Score

- Start at 100.
- Each finding subtracts by severity: `block` −15, `warn` −8, `info` −2 (cap total deductions at 100).
- Any `block` finding sets the gate to **BLOCKED** regardless of score.
- Deduplicate: one finding per (rule_id, file, line).

## 6. Output (exactly this shape)

```
🏷️  Musinsa Readiness Score: <N>/100   ·   Gate: <PASS | BLOCKED>
     rulebook: seed(<n>) + repo(<n>)  ·  changed files: <n>

<for each finding, worst severity first>
<❌ block | ⚠️ warn | ℹ️ info>  [<dimension>]  <file>:<line>   (<-points>)
   규칙: <title>   (<added_by>)
   근거: <rationale>
   👉  <fix>
   🔗  <source>

<if none>
✅ 룰북 위반 없음 — 모든 규칙 통과.
```

End with one line on what to do next (fix the blockers, or "/remember" a new rule if you spotted a recurring issue not yet in the rulebook). Be precise and terse; never invent a violation to pad the report.
