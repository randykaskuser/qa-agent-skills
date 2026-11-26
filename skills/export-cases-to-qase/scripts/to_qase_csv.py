#!/usr/bin/env python3
"""
Casely Markdown test cases -> Qase CSV (v1 format).

Reads a directory of Casely-style Markdown case files (one Markdown table per
file: header row, separator row, exactly one data row) and writes a single CSV
that Qase's importer accepts.

Qase's importer does not remap headers -- it reads the first row and refuses to
guess. So this script emits Qase's documented column names, not the team's.

Usage:
    python to_qase_csv.py results out.csv
    python to_qase_csv.py results out.csv --suite "Home / Player"
    python to_qase_csv.py results out.csv --template real_qase_export.csv
    python to_qase_csv.py results out.csv --map "Priorität=priority,Schritte=steps_actions"

Exit code is non-zero if any case was rejected. Nothing is written in that case,
so a partial import is never produced.
"""

import argparse
import csv
import re
import sys
from pathlib import Path

# Documented Qase CSV (v1) columns.
DEFAULT_HEADERS = [
    "id", "title", "description", "preconditions", "postconditions",
    "priority", "severity", "type", "behavior", "automation", "status", "layer",
    "is_flaky", "suite_id", "suite", "suite_parent_id", "suite_without_cases",
    "steps_actions", "steps_results", "steps_data",
]

# Allowed values per Qase docs. An out-of-range value fails the whole import,
# so we normalise to the documented default instead of passing it through.
ENUMS = {
    "priority": ({"undefined", "high", "medium", "low"}, "undefined"),
    "severity": ({"undefined", "blocker", "critical", "major", "normal",
                  "minor", "trivial"}, "undefined"),
    "type": ({"other", "functional", "smoke", "regression", "security",
              "usability", "performance", "acceptance", "compatibility",
              "integration", "exploratory"}, "functional"),
    "behavior": ({"undefined", "positive", "negative", "destructive"}, "undefined"),
    "automation": ({"is-not-automated", "to-be-automated", "automated"},
                   "is-not-automated"),
    "status": ({"draft", "actual", "deprecated"}, "actual"),
    "layer": ({"unknown", "e2e", "api", "unit"}, "e2e"),
    "is_flaky": ({"no", "yes"}, "no"),
}

# Common team header -> Qase column. Case- and punctuation-insensitive.
ALIASES = {
    "id": "id", "testcaseid": "id", "caseid": "id", "tcid": "id",
    "title": "title", "name": "title", "summary": "title", "testcase": "title",
    "description": "description", "objective": "description", "goal": "description",
    "precondition": "preconditions", "preconditions": "preconditions",
    "setup": "preconditions", "prerequisite": "preconditions",
    "prerequisites": "preconditions",
    "postcondition": "postconditions", "postconditions": "postconditions",
    "teardown": "postconditions", "cleanup": "postconditions",
    "step": "steps_actions", "steps": "steps_actions",
    "action": "steps_actions", "actions": "steps_actions",
    "teststeps": "steps_actions", "stepstoreproduce": "steps_actions",
    "expected": "steps_results", "expectedresult": "steps_results",
    "expectedresults": "steps_results", "result": "steps_results",
    "results": "steps_results", "expectedoutcome": "steps_results",
    "testdata": "steps_data", "data": "steps_data", "stepsdata": "steps_data",
    "priority": "priority", "severity": "severity", "type": "type",
    "casetype": "type", "testtype": "type",
    "behavior": "behavior", "behaviour": "behavior",
    "automation": "automation", "automationstatus": "automation",
    "status": "status", "layer": "layer", "level": "layer",
    "isflaky": "is_flaky", "flaky": "is_flaky",
    "suite": "suite", "module": "suite", "component": "suite",
    "feature": "suite", "section": "suite", "folder": "suite",
}

# Value synonyms seen in real team formats.
VALUE_SYNONYMS = {
    "priority": {"p0": "high", "p1": "high", "p2": "medium", "p3": "low",
                 "critical": "high", "highest": "high", "lowest": "low",
                 "hoch": "high", "mittel": "medium", "niedrig": "low",
                 "tinggi": "high", "sedang": "medium", "rendah": "low"},
    "layer": {"ui": "e2e", "gui": "e2e", "frontend": "e2e", "front-end": "e2e",
              "integration": "api", "system": "e2e", "component": "unit"},
    "behavior": {"positive": "positive", "negative": "negative",
                 "happy": "positive", "happypath": "positive",
                 "sad": "negative", "error": "negative"},
    "automation": {"manual": "is-not-automated", "no": "is-not-automated",
                   "yes": "automated", "auto": "automated",
                   "todo": "to-be-automated", "planned": "to-be-automated"},
    "type": {"negative": "functional", "boundary": "functional",
             "e2e": "functional", "ui": "functional", "api": "functional"},
}


def norm_key(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def split_row(line):
    """Split a Markdown table row, honouring \\| as a literal pipe."""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith(r"\|"):
        line = line[:-1]
    cells, buf, i = [], [], 0
    while i < len(line):
        ch = line[i]
        if ch == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            buf.append("|")
            i += 2
            continue
        if ch == "|":
            cells.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    cells.append("".join(buf).strip())
    return cells


def is_separator(cells):
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c.strip()) for c in cells if c.strip())


def parse_case(path):
    """Return (dict of raw header -> value, error string or None)."""
    rows = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if "|" not in raw:
            continue
        cells = split_row(raw)
        if is_separator(cells):
            continue
        rows.append(cells)
    if len(rows) < 2:
        return None, "no Markdown table with a header row and a data row"
    header, data = rows[0], rows[1]
    if len(rows) > 2:
        return None, (f"{len(rows) - 1} data rows found; each file must hold "
                      "exactly one case (a real newline inside a cell splits the row -- use <br>)")
    if len(data) != len(header):
        return None, (f"{len(header)} headers but {len(data)} cells -- an "
                      r"unescaped | shifts every value; escape it as \|")
    return dict(zip(header, data)), None


def step_lines(text):
    """<br> -> a list of step texts, with any existing numbering stripped."""
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    return [re.sub(r"^\d+[.)]\s*", "", ln.strip())
            for ln in text.split("\n") if ln.strip()]


def number(lines):
    return "\n".join("%d. %s" % (n, ln) for n, ln in enumerate(lines, 1))


def align_results(actions, results):
    """Qase v1 pairs steps_actions and steps_results line by line.

    A team format with three steps and one expected result is the common case;
    numbering that result as line 1 would attach it to the first step. Pad so it
    lands on the last step, which is where the check actually happens.
    """
    if not results or not actions or len(results) >= len(actions):
        return results
    return [""] * (len(actions) - len(results)) + results


def coerce(col, value, warnings, case_id):
    v = value.strip()
    if not v:
        return ""
    key = re.sub(r"[^a-z0-9-]", "", v.lower())
    key = VALUE_SYNONYMS.get(col, {}).get(key, key)
    allowed, default = ENUMS[col]
    if key in allowed:
        return key
    warnings.append(f"{case_id}: {col}={v!r} is not a Qase value; using {default!r}")
    return default


def main():
    ap = argparse.ArgumentParser(description="Casely Markdown cases -> Qase CSV")
    ap.add_argument("results_dir", help="directory of Casely .md case files")
    ap.add_argument("output", help="CSV file to write")
    ap.add_argument("--suite", default="", help="suite name for every case (nest with ' / ')")
    ap.add_argument("--template", help="a real Qase export CSV; its header row is used verbatim")
    ap.add_argument("--map", default="", help="explicit header mapping, 'Their Header=qase_column,...'")
    args = ap.parse_args()

    results = Path(args.results_dir)
    if not results.is_dir():
        sys.exit(f"error: {results} is not a directory")
    files = sorted(results.glob("*.md"))
    if not files:
        sys.exit(f"error: no .md case files in {results}")

    headers = DEFAULT_HEADERS
    if args.template:
        with open(args.template, newline="", encoding="utf-8-sig") as fh:
            headers = next(csv.reader(fh))
        print(f"Using header row from {args.template} ({len(headers)} columns)")

    overrides = {}
    for pair in filter(None, (p.strip() for p in args.map.split(","))):
        if "=" not in pair:
            sys.exit(f"error: --map entry {pair!r} is not 'Their Header=qase_column'")
        k, v = pair.split("=", 1)
        overrides[norm_key(k)] = v.strip()

    rows, errors, warnings, unmapped = [], [], [], set()

    for path in files:
        raw, err = parse_case(path)
        if err:
            errors.append(f"{path.name}: {err}")
            continue

        row = {h: "" for h in headers}
        case_id = ""
        actions, results = [], []
        for header, value in raw.items():
            col = overrides.get(norm_key(header)) or ALIASES.get(norm_key(header))
            if col is None:
                unmapped.add(header)
                continue
            if col == "id":
                case_id = value
                continue  # Qase assigns ids; the team id is preserved below.
            if col == "steps_actions":
                actions = step_lines(value)
            elif col == "steps_results":
                results = step_lines(value)
            elif col in ENUMS:
                # A "negative"/"destructive" test *type* is Qase's behavior field,
                # not its type field -- route it there instead of losing it.
                key = re.sub(r"[^a-z0-9-]", "", value.strip().lower())
                if col == "type" and key in ("negative", "positive", "destructive"):
                    row["behavior"] = key
                    row["type"] = "functional"
                else:
                    row[col] = coerce(col, value, warnings, case_id or path.name)
            elif col in row:
                row[col] = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)

        row["steps_actions"] = number(actions)
        row["steps_results"] = number(align_results(actions, results))

        if not row.get("title"):
            errors.append(f"{path.name}: no title column -- title is Qase's only required field")
            continue

        # Keep the team's own id traceable; Qase generates its own on import.
        if case_id:
            note = f"Source case: {case_id}"
            row["description"] = f"{row['description']}\n\n{note}".strip()

        if args.suite:
            row["suite"] = args.suite
        if not row.get("status"):
            row["status"] = "actual"
        rows.append(row)

    if unmapped:
        warnings.append("columns with no Qase equivalent, dropped: "
                        + ", ".join(sorted(unmapped))
                        + " (use --map, or add them as Qase custom fields first)")

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    if errors:
        print(f"\n{len(errors)} case(s) rejected -- nothing written:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    # Suite rows come first: Qase needs the suite to exist before cases reference it.
    out_rows = []
    if args.suite and "suite_without_cases" in headers:
        parts = [p.strip() for p in args.suite.split("/") if p.strip()]
        for depth, name in enumerate(parts, start=1):
            suite_row = {h: "" for h in headers}
            suite_row["suite_id"] = str(depth)
            suite_row["suite"] = name
            suite_row["suite_without_cases"] = "1"
            if depth > 1:
                suite_row["suite_parent_id"] = str(depth - 1)
            out_rows.append(suite_row)
        for r in rows:
            r["suite_id"] = str(len(parts))
            r["suite"] = parts[-1]
    out_rows.extend(rows)

    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote {len(rows)} test cases to {args.output}")
    if args.suite:
        print(f"Suite: {args.suite}")
    print("Import in Qase via Import -> Qase (CSV). Confirm the header row matches "
          "your workspace's template before a large import.")


if __name__ == "__main__":
    main()
