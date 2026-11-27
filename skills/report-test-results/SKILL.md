---
name: report-test-results
description: Use when a test run, platform comparison or exploration is finished and its results must be read or trusted by someone who was not there (PM, developers, another tester), or when another QA skill (test-a-ticket, consistency-check, explore-app-without-spec, verify-bug-fix) calls for a results page or before/after image. Not for running a bug retest itself (use verify-bug-fix). Not for test cases, coverage pages, code review or CI reports that already have their own format.
license: "MIT"
---

# Report Test Results

One light-theme page that answers, in this order: is it good, what was judged against, what happened to every item, what proves it, what was tested, what is still open.

## Steps

1. Read `python3 ${CLAUDE_PLUGIN_ROOT}/skills/report-test-results/scripts/report_test_results.py --help` and `scripts/spec.example.json`. If that path does not resolve, use the `scripts` folder beside this file.
2. Fill `spec.json` next to the screenshots, using the row for your run type:

| Run | columns | one row per | figure per | table |
|---|---|---|---|---|
| Ticket test | `Result` | checklist item | failed item, with its repro card | test data and how it was left |
| Platform comparison | the platforms | compared item | differing item, panels side by side | records tested |
| Permission test | menu, route, API, after re-login | case | failed case | actors and restored state |
| Exploration | `Observed` | behaviour, question, anomaly | anomaly | areas explored |
| Fix retest (before/after) | `retest`: Check, Before, After | check, per ticket | — (each check carries its own crops) | — |

   For a fix retest, fill `retest` (one entry per ticket; `rows` may be left out):
   - **Header:** ticket id and `title` copied word for word from the tracker ticket, then the "QA passed" pill. Passed retests only; verify-bug-fix handles a fix that still fails.
   - **`sub`:** environment, date, and the viewer and event timezones when they matter.
   - **Rows:** in the order the user does them.
   - **Before:** the bug in red: what the user saw at that step before the fix, from the bug report or what the bug caused there. When the bug stopped the user reaching the step, say so ("Couldn't get here: the code came back"); "No … before" for something new. Reuse the earlier bug-report proof image as `before_image` when one exists, keeping its marks.
   - **After:** the retest in green, with a crop of the retest screenshot as `after_image`. A check the user sees on screen needs a sharp screenshot; text only is for evidence with no screen, such as an API response.
   - Crop the same region from both screenshots, only the part that changed: no full-page shots, no sidebars or personal data. Before and After render at the same width, so equal crops line up. Mark the after crop with a `GRN` box from `compare_panels.py` when the change is small.
   - `comment`: the one-line tracker comment that goes with the PNG.
3. Crop and mark screenshots with `compare_panels.py` (same folder). No personal data or tokens in an image or in `evidence`.
4. Build; add `--png` for a fix retest. It also writes `<id>-before-after.png` (light theme, plus its HTML) per ticket next to the page, rendered with headless Chrome. Post each PNG with its one-line `comment` on the Linear or Jira ticket. The script writes nothing until every red cell names its source and every figure has a date and proof; fix the spec, not the script.
5. **Review before handing over, every run type.** Give a fresh subagent only the page text (or, for a fix retest, the PNG) and the ticket text, not your reasoning; with no subagent, read it yourself as the reader would. It writes down its answers to the five questions in "The page contract" below, from the page alone, and quotes every word it does not understand. Any "can't tell" or unexplained number is a fix. For a fix retest it also checks each PNG:
   - the title is the ticket's title, word for word;
   - rows are in the order the user does them;
   - each image shows exactly what its cell says, on the right record;
   - every image is sharp at full size and has no personal data;
   - every Before says what happened before.

   Fix the spec or retake the screenshot, rebuild, and review again until every answer is on the page. When a shot cannot be retaken, tell the user before posting: weak proof does not change the verdict, it holds the post until a retake or the user's go-ahead. The PNGs and their comments are what you hand over; publish the page only when asked.
6. Otherwise, open the page once. Then publish it private with the Artifact tool, or send the HTML file where there is none. On a rerun, republish to the same URL.

## The page contract

A reader who was not there answers five questions from the page alone. Fill the spec so each answer is on it:

1. **What happened, and what do I do?** `lead`: sentence one is the verdict (ready or not, the count); sentence two is what the reader must do or decide ("approve 2 tickets, answer 2 questions", or "nothing"). Then build or environment and date.
2. **What do the numbers count?** Each stat counts a real thing that its label names: "Bugs filed", "Need a decision", "Contests run", not table rows. Numbers that should add up do; when two rows share one bug, the stat's note says so.
3. **Which ticket covers what?** Once tickets exist, their cards come first, and every row and figure a ticket covers names it as "TICKET #n" (n = the bug's number in that ticket; the ticket id alone when its bugs are not numbered). A row no ticket covers says why, for example "none: needs a decision".
4. **Are the words mine?** Name rows and figures by what the user sees, in plain words. Internal codes (B1, W9, "lead 3"), record IDs and environment codenames stay off the page, or are explained once where they first appear.
5. **What is still open?** `open` lists every action or decision, each with who: questions for developers, the proposed standard for each observed difference, checks not run, test data to clean up.

Blocked and not-run items are rows too, so the totals match the checklist. A question for developers is a `b` row, reworded with `legend` ({"b": "question or not checked"}); an item that does not exist on one platform gets an `n` cell, "Not on this platform". Anything else the reader needs goes in `sections`; never edit the built HTML, because the next build loses it.
