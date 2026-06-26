#!/usr/bin/env python3
"""제출용 submission.zip 생성 — 최종 제출 직전에 실행해 최신 logs를 포함시킨다.
  python3 tools/pack_submission.py
필수(src/README/logs) + 보너스(demo/docs/LICENSE/.agents)를 담는다. zip CLI 불필요.
"""
import zipfile, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INCLUDE = ["src", "README.md", "logs", "demo", "docs", "LICENSE", ".agents"]
EXCLUDE_PARTS = {"__pycache__", ".git"}
OUT = os.path.join(ROOT, "submission.zip")

def skip(p):
    return any(part in EXCLUDE_PARTS for part in p.split(os.sep)) or p.endswith((".pyc", ".DS_Store"))

def main():
    os.chdir(ROOT)
    if os.path.exists(OUT):
        os.remove(OUT)
    n = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for item in INCLUDE:
            if not os.path.exists(item):
                print("  (skip, not found):", item); continue
            if os.path.isfile(item):
                if not skip(item):
                    z.write(item); n += 1
            else:
                for root, _, files in os.walk(item):
                    if skip(root):
                        continue
                    for f in files:
                        fp = os.path.join(root, f)
                        if not skip(fp):
                            z.write(fp); n += 1
    print(f"submission.zip 생성: {n} files, {round(os.path.getsize(OUT)/1024,1)} KB")

if __name__ == "__main__":
    main()
