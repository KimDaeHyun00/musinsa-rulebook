---
name: remember
description: >
  Capture a coding rule / lesson into the shared team rulebook so future reviews
  enforce it on everyone. Works two ways: (A) with an explicit rule —
  "/remember money must use BigDecimal", "이거 규칙으로 기억해", "팀 룰에 추가해"; or
  (B) with NO argument — a bare "/remember" right after you fixed a bug or corrected
  AI-written code that broke a team norm: the skill infers the rule from the recent
  session work (git diff + the conversation) and proposes it. Appends a structured
  rule to the repo's .musinsa/rules.yaml (the repo layer of the cascading rulebook).
---

# Musinsa Rulebook — Remember

You turn a lesson into a structured rule that the `review` skill enforces on every
teammate's agent. The rule goes into the repo and travels through normal git/PR
review, growing the rulebook **without rebuilding or redistributing the plugin**.

Write the rule's `title` / `rationale` / `fix` in the **same language as the existing
rulebook** (the seed rules are Korean — match them), and reply to the user in their
own language.

## 1. Get the lesson — two modes

**Mode A — explicit.** The user gave a rule after `/remember`
(e.g. "결제 금액은 double 금지, BigDecimal"). Use that text as the lesson.

**Mode B — no argument (infer from the session).** A bare `/remember`. The user just
did something worth remembering (fixed a bug, or corrected AI-written code that broke a
Musinsa team norm) and wants it captured without retyping it. Reconstruct it:

1. Look at the **most recent change**: run `git diff`, `git diff --staged`, and if the
   fix was already committed, `git diff HEAD~1 HEAD`. Identify the files just touched.
2. Read it together with the **recent conversation** in this session — what was wrong
   and what was fixed.
3. In a fix diff, the **removed** lines usually reveal the **anti-pattern to forbid**;
   the **added** lines reveal the **preferred fix**. Form the lesson as
   "avoid <removed>, prefer <added>, because <reason>."
4. **Generalize** — capture the reusable rule, not this one instance. Do not hardcode
   this file's class/variable names into the rule.

If you cannot find a recent change or a clear lesson, ask the user **one** short
question rather than inventing a rule.

## 2. Build the rule object

```yaml
- id: <kebab-case, derived from the lesson, unique>
  dimension: <query-index | design-coupling | refactor-safety | cache-reliability | testing | convention | security | other>
  severity: <block | warn | info>      # default warn; block only for "must never ship"
  title: "<one line, imperative>"
  applies_to: ["<glob>", ...]          # infer from where it happened; default ["**/*"]
  detect:
    patterns: ["<regex>", ...]          # derive from the anti-pattern (removed/bad code) when mechanically catchable; else []
    llm_hint: "<what to look for in a diff>"
  rationale: "<why — the failure it prevents; include a metric/incident if known>"
  fix: "<how to comply — the preferred pattern>"
  source: "<Mode A: where the lesson came from; Mode B: 'session <YYYY-MM-DD> — inferred from <files/commit>'>"
  added_by: "<the current user — use `git config user.name` or the OS username; never the literal 'current user'>"
  added_at: "<YYYY-MM-DD if known>"
```

## 3. Confirm before writing

Always show the proposed rule (the YAML block). For **Mode B (inferred)**, first state
your reasoning in one line — e.g. *"최근 변경에서 `double 금액` → `BigDecimal` 수정을
확인했고, 이를 규칙으로 일반화했습니다"* — then ask the user to **confirm or adjust**
before committing; inference can be wrong, so do not write silently. For **Mode A**,
show it and proceed unless it is ambiguous.

## 4. Append to the repo rulebook

- Target: `.musinsa/rules.yaml` in the repo root.
- If it does not exist, create it with this header, then add the rule under `rules:`:

```yaml
# Musinsa Rulebook — REPO layer (team-owned, grown via the `remember` skill)
# Overrides same-id rules from the seed layer. Share by committing through a PR.
version: 1
layer: repo
rules: []
```

- Append the new rule. On `id` collision, refine the id, or — if it is genuinely the
  same rule being updated — replace it and note the change.

## 5. Confirm + share

Show the user the rule you added (the YAML) and remind them it becomes active for the
whole team once merged: commit `.musinsa/rules.yaml` and open a PR — **rule changes go
through review just like code**, which keeps the rulebook clean. Note that the next
`review` run already enforces it locally before the PR merges.
