---
name: build-proof-page
description: Use when a test run, platform comparison or exploration is finished and its results must be read or trusted by someone who was not there (PM, developers, another tester), or when another QA skill calls for a proof page. Not for test cases, coverage pages, code review or CI reports that already have their own format.
license: "MIT"
---

# Build Proof Page

One light-theme page that answers, in this order: is it good, what was judged against, what happened to every item, what proves it, what was tested, what is still open.

## Steps

1. Read `python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-proof-page/scripts/build_proof_page.py --help` and `scripts/spec.example.json`. If that path does not resolve, use the `scripts` folder beside this file.
2. Fill `spec.json` next to the screenshots, using the row for your run type:

| Run | columns | one row per | figure per | table |
|---|---|---|---|---|
| Ticket test | `Result` | checklist item | failed item, with its repro card | test data and how it was left |
| Platform comparison | the platforms | compared item | differing item, panels side by side | records tested |
| Permission test | menu, route, API, after re-login | case | failed case | actors and restored state |
| Exploration | `Observed` | behaviour, question, anomaly | anomaly | areas explored |

3. Crop and mark screenshots with `compare_panels.py` (same folder). No personal data or tokens in an image or in `evidence`.
4. Build. The script writes nothing until every red cell names its source and every figure has a date and proof; fix the spec, not the script.
5. Open the page once. Then publish it private with the Artifact tool, or send the HTML file where there is none. On a rerun, republish to the same URL.

`lead` states the verdict first: ready or not, the count, build and date. Blocked and not-run items are rows too, so the totals match the checklist.
