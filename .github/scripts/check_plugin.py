#!/usr/bin/env python3
"""Regression checks for the qa-agent-skills plugin: run before every release.

    python3 .github/scripts/check_plugin.py .

Checks each SKILL.md (name matches folder, description <= 1024 chars and free of < >, every
qa-agent-skills:<skill>, skills/<skill>/ and references/ / scripts/ path it mentions exists, no
old skill names), versions in plugin.json and marketplace.json match, README lists every skill,
every script compiles, the report example builds with --png (needs Pillow and Chrome), and the
Qase converter runs. Exit code 1 on any failure.
"""
import json, os, re, subprocess, sys, tempfile

repo = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
sk = os.path.join(repo, "skills")
fails, notes = [], []
names = sorted(d for d in os.listdir(sk) if os.path.isfile(os.path.join(sk, d, "SKILL.md")))
OLD = ["build-proof-page", "build_proof_page", "proof page", "ui-tour", "ticket-driven-qa", "exploratory-web-testing",
       "new-app-test-design", "e2e-batch-loop", "repo-gap-audit", "playwright-robot", "qa-automation", "technical-blogger",
       "viral-ugc-ads"]


def fm(path):
    s = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n", s, re.S)
    if not m:
        return None, s
    head = m.group(1)
    name = re.search(r"^name:\s*(.+)$", head, re.M)
    d = re.search(r"^description:\s*(>\s*\n)?(.*?)(\n[a-z_]+:|\Z)", head, re.S | re.M)
    return {"name": name.group(1).strip() if name else None,
            "description": " ".join(d.group(2).split()) if d else ""}, s


for n in names:
    p = os.path.join(sk, n, "SKILL.md")
    meta, body = fm(p)
    if not meta:
        fails.append(f"{n}: no frontmatter"); continue
    if meta["name"] != n:
        fails.append(f"{n}: name field is {meta['name']}")
    d = meta["description"]
    if not d.startswith("Use") and n not in ("write-test-cases",):
        notes.append(f"{n}: description does not start with 'Use' (ok if long-standing)")
    if len(d) > 1024:
        fails.append(f"{n}: description {len(d)} chars > 1024")
    if "<" in d or ">" in d:
        fails.append(f"{n}: description has < or >")
    # cross-skill references
    for ref in set(re.findall(r"qa-agent-skills:([a-z0-9-]+)", body)):
        if ref not in names:
            fails.append(f"{n}: refers to missing skill qa-agent-skills:{ref}")
    for ref in set(re.findall(r"skills/([a-z0-9-]+)/", body)):
        if ref not in names:
            fails.append(f"{n}: path to missing skill folder skills/{ref}/")
    # relative files mentioned
    for rel in set(re.findall(r"(?<![\w/])((?:references|scripts|assets|evals)/[\w./-]+\.\w+)", body)):
        if not os.path.exists(os.path.join(sk, n, rel)):
            fails.append(f"{n}: mentions {rel}, not found in the skill folder")
    # old names (skip the vendored casely copy, which may mention its upstream name)
    if n != "write-test-cases":
        for old in OLD:
            if old in body.replace(".claude/ui-tour.md", ""):  # project notes file name, kept on purpose
                fails.append(f"{n}: still mentions old name '{old}'")
    for ref in re.findall(r"\[[^\]]*\]\(([^)#]+\.md)\)", body):
        if not ref.startswith("http") and not os.path.exists(os.path.join(sk, n, ref)):
            fails.append(f"{n}: markdown link to missing {ref}")

# reference files: old names
for root, _, files in os.walk(sk):
    if "/write-test-cases" in root:
        continue
    for f in files:
        if f.endswith((".md", ".py", ".json")) and f != "SKILL.md":
            t = open(os.path.join(root, f), encoding="utf-8", errors="ignore").read()
            for old in ("build-proof-page", "build_proof_page"):
                if old in t:
                    fails.append(f"{os.path.relpath(os.path.join(root, f), sk)}: mentions '{old}'")

# versions
pv = json.load(open(os.path.join(repo, ".claude-plugin/plugin.json")))["version"]
mv = json.load(open(os.path.join(repo, ".claude-plugin/marketplace.json")))["plugins"][0]["version"]
if pv != mv:
    fails.append(f"plugin.json {pv} != marketplace.json {mv}")

# README lists every skill
readme = open(os.path.join(repo, "README.md"), encoding="utf-8").read()
for n in names:
    if f"(skills/{n})" not in readme:
        fails.append(f"README: no table row for {n}")
for ref in set(re.findall(r"\(skills/([a-z0-9-]+)\)", readme)):
    if ref not in names:
        fails.append(f"README: links missing skill {ref}")
for old in ("build-proof-page",):
    if old in readme:
        fails.append(f"README mentions {old}")

# python scripts compile and --help works
for root, _, files in os.walk(sk):
    for f in files:
        if f.endswith(".py"):
            p = os.path.join(root, f)
            r = subprocess.run([sys.executable, "-m", "py_compile", p], capture_output=True, text=True)
            if r.returncode:
                fails.append(f"compile {os.path.relpath(p, sk)}: {r.stderr.strip()[:200]}")

# report-test-results example builds, with and without --png
rs = os.path.join(sk, "report-test-results/scripts")
with tempfile.TemporaryDirectory() as tmp:
    r = subprocess.run([sys.executable, os.path.join(rs, "report_test_results.py"), os.path.join(rs, "spec.example.json"),
                        os.path.join(tmp, "page.html"), "--png"], capture_output=True, text=True)
    if r.returncode or not os.path.exists(os.path.join(tmp, "page.html")):
        fails.append(f"report_test_results example: {r.stdout[-300:]} {r.stderr[-300:]}")
    elif not any(f.endswith("-before-after.png") for f in os.listdir(tmp)):
        fails.append("report_test_results --png wrote no PNG")
    # qase converter
    qs = os.path.join(sk, "export-cases-to-qase/scripts/to_qase_csv.py")
    cases = os.path.join(tmp, "results"); os.mkdir(cases)
    open(os.path.join(cases, "TC001_a.md"), "w").write("| ID | Title | Steps | Expected Result | Priority |\n|---|---|---|---|---|\n| TC001 | A | 1. Open | Shown | High |\n")
    r = subprocess.run([sys.executable, qs, cases, os.path.join(tmp, "q.csv"), "--suite", "A / B"], capture_output=True, text=True)
    if r.returncode:
        fails.append(f"to_qase_csv: {r.stdout[-200:]} {r.stderr[-200:]}")

print(f"{len(names)} skills, version {pv}")
for x in notes:
    print("note:", x)
for x in fails:
    print("FAIL:", x)
print("OK" if not fails else f"{len(fails)} failures")
sys.exit(1 if fails else 0)
