---
name: export-cases-to-qase
description: Use when test cases written as Markdown (write-test-cases / Casely `results/` files, or cases from explore-app-without-spec) must go into Qase as a CSV import, or when a Qase CSV import fails or drops columns because of its header row. Not for writing the cases themselves (use write-test-cases) or recording run results in Qase.
license: "MIT"
---

# Export Cases to Qase

Turn Markdown test cases into one CSV that Qase's importer accepts.

**Core rule:** Qase reads the first row to decide what each column is and does not guess. It refuses a renamed, missing or reordered header. That is the opposite of write-test-cases' "keep the team's exact headers" rule; the two agree only when the team's format already is Qase's.

## Steps

1. **Get a real Qase export if the user can give one** (any CSV exported from their workspace). It carries their custom fields and their Qase version's step format, which no fixed list can.
2. **Convert:**

   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/export-cases-to-qase/scripts/to_qase_csv.py \
     results qase_import.csv --suite "Parent / Child"
   ```

   If that path does not resolve, use the `scripts` folder beside this file.
   - `--template real_qase_export.csv`: take the header row from the user's export. Use it whenever step 1 found one.
   - `--map "Schritte=steps_actions,Priorität=priority"`: columns the alias table misses.
   - `--suite "Parent / Child"`: writes the suite rows first; Qase needs them before cases can reference them.
3. **Read every warning.** A rejected case stops the whole file, with the file name and reason: fix the case and rerun. A dropped column disappears from the import unless a matching custom field exists in Qase first: name each one to the user.
4. **Hand over** the CSV with the counts (cases, suites), the dropped columns, and what the converter changed: a test type moved to `behavior`, one expected result placed on the last step (see "What the converter does" in the reference). Never call a partial export complete.

Column list, allowed values, and what is documented versus inferred: [references/qase-csv.md](references/qase-csv.md). The script is standard library only, with no network calls.

## Common mistakes

| Mistake | Fix |
|---|---|
| Team's own headers kept | Qase's names, or `--template` |
| Suites missing | `--suite`, so suite rows come first |
| Dropped-column warning ignored | Tell the user; create the custom field first |
| Run results pushed as cases | This is for cases; results go through Qase runs |
