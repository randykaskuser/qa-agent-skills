# Adapter — test management tools (optional)

Most ad-hoc QA runs end in the tracker, not a test-management tool. Use this file only when the
project actually keeps a suite there, or when the user asks for the run to be recorded.

Decide which of these you are doing — they are different jobs:

- **Record this run's results** against existing cases → a test run.
- **Turn this run into lasting regression cases** → that is the `exploratory-web-testing` skill's
  job. Hand it the checklist and observed values from Phase 7; don't hand-write cases here.

## Qase

Via a Qase MCP connector, or the REST API at `https://api.qase.io/v1` with a `Token` header.

| Job | Call |
|---|---|
| Find the project and its suites | `qase_project_context` |
| Search existing cases | `qql_search` (see `qql_help` for the query syntax) |
| Create or update a case | `qase_case_upsert` |
| Open a run | `qase_run_upsert` |
| Record a result | `qase_result_record` — status `passed` / `failed` / `blocked` / `skipped` |
| File a defect from a failure | `qase_defect_upsert`, or `qase_triage_defect` |
| Attach evidence | `qase_attachment_upload` |
| Push a whole CI report | `qase_ci_report` |

Map the Phase 7 vocabulary straight across: pass → `passed`, fail → `failed`, blocked → `blocked`,
not run → `skipped`. **Partial has no equivalent** — record it as `failed` or `blocked` and put
what was and wasn't covered in the comment. Don't quietly round a partial up to a pass.

For bulk import of new cases, the CSV route is usually faster than the API. Qase's importer will
not remap headers, so use the converter in the `exploratory-web-testing` skill
(`scripts/to_qase_csv.py`), which emits Qase's own column names.

## TestRail

REST API at `/index.php?/api/v2/…`, basic auth with an API key.

| Job | Endpoint |
|---|---|
| Cases in a suite | `get_cases/{project_id}&suite_id={id}` |
| Create a case | `add_case/{section_id}` |
| Open a run | `add_run/{project_id}` |
| Record results | `add_results_for_cases/{run_id}` |
| Close the run | `close_run/{run_id}` |

Status IDs are per-instance. Read them with `get_statuses` — do not hardcode the defaults.

## Zephyr

Zephyr Scale and Zephyr Squad have different APIs and both sit inside Jira. Read the instance's
own API docs before writing anything; the endpoint shapes differ enough that guessing wastes a run.
If the project uses Zephyr, record results through the Jira adapter and let the user mirror them,
unless they explicitly ask for the Zephyr API.

---

## No test-management tool

That is the common case, and it is fine. The QA ticket's checklist **is** the test case list, and
the results comment **is** the run record. Say so in the final reply rather than inventing a tool.
