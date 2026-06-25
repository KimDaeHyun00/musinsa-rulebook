---
name: remember
description: >
  Capture a coding rule / lesson into the shared team rulebook so future reviews
  enforce it on everyone. Use when the user says "/remember ...", "이거 규칙으로 기억해",
  "팀 룰에 추가해", "다음부턴 이렇게 하도록 규칙 넣어줘", or after fixing a bug whose
  root cause should never recur. Appends a structured rule to the repo's
  .musinsa/rules.yaml (the repo layer of the cascading rulebook).
---

# Musinsa Rulebook — Remember

You turn a human's lesson ("from now on, money must use BigDecimal, not double")
into a structured rule that the `review` skill can enforce on every teammate's agent.
The rule goes into the repo, travels through normal git/PR review, and grows the
rulebook **without rebuilding or redistributing the plugin**.

## 1. Understand the lesson

From the user's words (and the surrounding diff/conversation if relevant), extract:
- **what** is the rule (the invariant to enforce),
- **why** (rationale — the failure it prevents; include a metric/incident if known),
- **where** it applies (file globs / a domain like `payment/**`),
- **how to comply** (the fix/pattern),
- **how to detect** it: a regex if mechanically catchable, otherwise an `llm_hint`.

Ask one brief clarifying question only if the rule is too vague to detect or apply. Otherwise infer sensible defaults.

## 2. Build the rule object

```yaml
- id: <kebab-case, derived from the lesson, unique>
  dimension: <query-index | design-coupling | refactor-safety | cache-reliability | testing | convention | security | other>
  severity: <block | warn | info>      # default warn; use block only for "must never ship"
  title: "<one line, imperative>"
  applies_to: ["<glob>", ...]          # default ["**/*"] if unknown
  detect:
    patterns: ["<regex>", ...]          # [] if not mechanically detectable
    llm_hint: "<what to look for in a diff>"
  rationale: "<why — failure prevented, metric/incident if any>"
  fix: "<how to comply>"
  source: "<PR/commit/url/conversation — where this lesson came from>"
  added_by: "<current user/handle>"
  added_at: "<YYYY-MM-DD if known>"
```

## 3. Append to the repo rulebook

- Target: `.musinsa/rules.yaml` in the repo root.
- If it does not exist, create it with this header, then add the rule under `rules:`:

```yaml
# Musinsa Rulebook — REPO layer (team-owned, grown via the `remember` skill)
# Overrides same-id rules from the seed layer. Share by committing through a PR.
version: 1
layer: repo
rules: []
```

- Append the new rule. If an `id` collides, either refine the id or, if it is genuinely the same rule being updated, replace it and note the change.

## 4. Confirm + share

Show the user the rule you added (the YAML block) and remind them it becomes active
for the whole team once merged: commit `.musinsa/rules.yaml` and open a PR — **rule
changes go through review just like code**, which keeps the rulebook clean. Mention
that the next `review` run will already enforce it locally before the PR merges.
