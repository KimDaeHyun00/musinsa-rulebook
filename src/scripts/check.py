#!/usr/bin/env python3
"""Deterministic first pass for the Musinsa Rulebook `review` skill.

Loads one or more rulebook YAML files (cascading: later files override same `id`),
scans the given files for each rule's `detect.patterns` (regex), and prints JSON
hits: [{rule_id, dimension, severity, title, file, line, snippet, source}].

This is the reproducible half of the hybrid score — pattern-catchable rules never
drift between runs. Design-judgment rules (empty patterns, llm_hint only) are left
to the agent.

Usage:
  python3 check.py --rules seed.yaml [--rules repo.yaml ...] --files a.java b.sql ...
"""
import argparse, json, re, sys, os

def load_rules(paths):
    try:
        import yaml
    except ImportError:
        sys.stderr.write("NEED_PYYAML: pip install pyyaml (falling back to agent-only review)\n")
        return None
    merged = {}
    for p in paths:
        if not p or not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
        for rule in (doc.get("rules") or []):
            rid = rule.get("id")
            if rid:
                merged[rid] = rule  # later path wins
    return list(merged.values())

def scan(rules, files):
    hits = []
    for path in files:
        if not os.path.exists(path) or os.path.isdir(path):
            continue
        try:
            text = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for rule in rules:
            for pat in (rule.get("detect", {}) or {}).get("patterns", []) or []:
                try:
                    rx = re.compile(pat)
                except re.error:
                    continue
                for m in rx.finditer(text):
                    line = text.count("\n", 0, m.start()) + 1
                    snippet = text[m.start():m.start() + 120].splitlines()[0].strip()
                    hits.append({
                        "rule_id": rule.get("id"),
                        "dimension": rule.get("dimension"),
                        "severity": rule.get("severity", "warn"),
                        "title": rule.get("title"),
                        "file": path,
                        "line": line,
                        "snippet": snippet,
                        "rationale": rule.get("rationale"),
                        "fix": rule.get("fix"),
                        "source": rule.get("source"),
                        "added_by": rule.get("added_by", "seed"),
                    })
                    break  # one hit per (rule, file) is enough to flag
    return hits

POINTS = {"block": 15, "warn": 8, "info": 2}
ICON = {"block": "❌", "warn": "⚠️", "info": "ℹ️"}

def report(rules, hits, n_files):
    order = {"block": 0, "warn": 1, "info": 2}
    hits = sorted(hits, key=lambda h: (order.get(h["severity"], 3), h["file"], h["line"]))
    deduction = min(100, sum(POINTS.get(h["severity"], 0) for h in hits))
    score = 100 - deduction
    gate = "BLOCKED" if any(h["severity"] == "block" for h in hits) else "PASS"
    seed_n = sum(1 for r in rules if r.get("added_by", "seed") == "seed")
    repo_n = len(rules) - seed_n
    out = []
    out.append(f"\U0001f3f7️  Musinsa Readiness Score: {score}/100   ·   Gate: {gate}")
    out.append(f"     rulebook: seed({seed_n}) + repo({repo_n})  ·  changed files: {n_files}\n")
    if not hits:
        out.append("✅ 룰북 위반 없음 — 모든 규칙 통과.")
        return "\n".join(out)
    for h in hits:
        out.append(f"{ICON.get(h['severity'],'')}  [{h['dimension']}]  {h['file']}:{h['line']}   (-{POINTS.get(h['severity'],0)})")
        out.append(f"   규칙: {h['title']}   ({h['added_by']})")
        if h.get("rationale"): out.append(f"   근거: {h['rationale']}")
        if h.get("fix"):       out.append(f"   \U0001f449  {h['fix']}")
        if h.get("source"):    out.append(f"   \U0001f517  {h['source']}")
        out.append("")
    return "\n".join(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", action="append", default=[], help="rulebook YAML (repeatable; later overrides)")
    ap.add_argument("--files", nargs="*", default=[])
    ap.add_argument("--report", action="store_true", help="print scored human report instead of JSON")
    args = ap.parse_args()
    rules = load_rules(args.rules)
    if rules is None:
        print(json.dumps({"error": "pyyaml_missing", "hits": []}))
        return 0
    hits = scan(rules, args.files)
    if args.report:
        print(report(rules, hits, len(args.files)))
    else:
        print(json.dumps({"rule_count": len(rules), "hits": hits}, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
