# Qase CSV import

## The constraint

Qase's importer reads the first row to decide what each column is, and **does not guess**. A
renamed, missing, or reordered header fails the import rather than being remapped.

This is the opposite of Casely's core rule, which is to preserve the team's own headers exactly
so their TMS mapping keeps working. Both are right for their own tool. They only agree when the
team's example test-case file already *is* a Qase export — which is why, for a Qase workspace,
the style example handed to Casely should be a real Qase CSV export.

`title` is the only mandatory field. Everything else takes a documented default when empty.

## Columns

Documented property columns:

| Column | Values |
|--------|--------|
| `id` (v1) / `v2.id` (v2) | Row identifier; Qase assigns real case ids on import |
| `title` | **Required.** Free text |
| `description` | Free text |
| `preconditions` | Free text |
| `postconditions` | Free text |
| `priority` | `undefined`, `high`, `medium`, `low` |
| `severity` | `undefined`, `blocker`, `critical`, `major`, `normal`, `minor`, `trivial` |
| `type` | `other`, `functional`, `smoke`, `regression`, `security`, `usability`, `performance`, `acceptance`, `compatibility`, `integration`, `exploratory` |
| `behavior` | `undefined`, `positive`, `negative`, `destructive` |
| `automation` | `is-not-automated`, `to-be-automated`, `automated` |
| `status` | `draft`, `actual`, `deprecated` |
| `layer` | `unknown`, `e2e`, `api`, `unit` |
| `is_flaky` | `no`, `yes` |
| `is_muted` | `yes` (empty means unchecked) |

Steps — all steps for a case live in these columns, never spread across rows:

| Column | Purpose |
|--------|---------|
| `steps_actions` | The step text |
| `steps_results` | Expected result, paired line by line with the actions |
| `steps_data` | Data needed to perform each step |

Suites:

| Column | Purpose |
|--------|---------|
| `suite_id` | Sequential id assigned in the file (1, 2, 3…) |
| `suite` | Suite name |
| `suite_parent_id` | The `suite_id` of the parent, for nesting |
| `suite_without_cases` | `1` marks the row as a suite definition, not a test case |

Suites must be defined before the cases that reference them, so suite rows go first in the file.

## Step format versions

- **v1** (deprecated but widely used): plain numbered text, one step per line, first column `id`.
- **v2** (current): step content specially encoded to survive commas, line breaks and special
  characters; first column `v2.id`; supports nested steps via tab indentation.

The bundled converter writes **v1**, because it is readable and diff-able. If the workspace is on
v2, or uses custom fields, pass `--template` with a real export so the header row comes from the
workspace itself rather than from this table.

## What the converter does

`scripts/to_qase_csv.py` reads Casely's `results/*.md` files and writes one CSV.

- Maps common team header names to Qase columns via an alias table; `--map` overrides it.
- Converts `<br>` to real newlines and renumbers steps as v1 expects.
- **Aligns expected results to the last step.** Three steps and one expected result is the usual
  team format; numbering that result as line 1 would attach it to the first step, so it is padded
  to land on the step where the check actually happens.
- **Routes a `negative` / `positive` / `destructive` test *type* to `behavior`**, since Qase's
  `type` field has no such values and the information would otherwise be dropped.
- Normalises out-of-range enum values to the documented default and warns, rather than emitting a
  value that fails the whole import. Also maps common synonyms — `P1`→`high`, `UI`→`e2e`,
  `manual`→`is-not-automated`.
- Preserves the team's original case id in `description` as `Source case: TC001`, since Qase
  assigns its own ids on import.
- Emits suite rows first when `--suite` is given, nesting on ` / `.
- **Refuses the whole file** if any case is malformed, naming the file and the reason. A partial
  import is never produced.
- Warns about columns with no Qase equivalent. Those disappear from the import unless the
  matching custom field is created in Qase first.

## Verify before a large import

The column list above is assembled from Qase's published documentation, not from a live
workspace. Before importing hundreds of cases, run one case through and confirm it lands
correctly — or better, export a few existing cases from the workspace and pass that file with
`--template` so the header row is exactly the one Qase expects.

## Sources

- [Import test cases](https://docs.qase.io/general/get-started-with-the-qase-platform/test-cases/import-test-cases)
- [Qase CSV: a walkthrough guide](https://docs.qase.io/en/articles/14596319-qase-csv-a-walkthrough-guide)
- [Qase CSV: creating tests](https://docs.qase.io/en/articles/14442571-qase-csv-creating-tests)
- [Qase CSV: test case properties](https://docs.qase.io/en/articles/14423241-qase-csv-test-case-properties)
- [Qase CSV: adding test steps](https://docs.qase.io/en/articles/14441496-qase-csv-adding-test-steps)
- [Qase CSV: create suites](https://docs.qase.io/en/articles/14442561-qase-csv-create-suites)
