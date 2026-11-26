---
name: consistency-check
description: Use when the same flow, screen or feature must look and behave the same across platforms or builds (web, Android, iOS, staging vs production) and you need screenshot proof of what differs. Also use when a comparison table or bug list rests on screenshots that may be stale, taken in different states, or have no stated source of truth.
license: "MIT"
---

# Consistency Check

Compare one flow across platforms with marked, side-by-side screenshots judged against a named source of truth.

**Core rule:** a difference is only a bug against a source of truth. Without one, it is "observed".

## Steps

1. **Source of truth, per item.** Order: ticket mock or acceptance criteria, design file, majority of platforms, none. Write each rule with where it came from. "No mock found" is valid: label the item *observed*.
2. **State matrix first.** Rows are items, columns platforms. Every cell names the same record, step, typed input, selection, theme and language.
3. **Capture** each platform in its cell. Note build, version, date. Crop to what matters.
4. **Mark.** Red differs from the source, green matches, amber is a different pattern with no source. One short label per box; never cover the text you mark.
5. **Compare.** One image per item, platforms side by side, one caption line each. Add a table of all items.
6. **Re-verify.** Retest every claim the day you publish. A deploy can fix a bug overnight.
7. **Build the page.** **REQUIRED SUB-SKILL:** use qa-agent-skills:report-test-results (run type: platform comparison). In the spec: one `stats` entry per platform with its count of differences, `rule` naming the source of truth used, and the record and date on every figure.
8. **Propose, then stop.** Reply with the page link and a list to approve: one parent ticket per platform with its numbered bugs (Expected, Actual, Steps, source of truth, test case ID, proof link), and each existing bug the retest shows fixed. End the turn with the question which of these to create or close.
9. **File what was approved,** add the ticket links to the spec and republish to the same URL.

`compare_panels.py` in report-test-results draws the boxes and builds the side-by-side images.

## Before publishing

| Check | Fail looks like |
|---|---|
| Same record | One platform shows a 4-checkbox contest, the others 2 |
| Same input | One panel typed, the others empty |
| Same selection | One answer picked, the others not |
| Same moment | One panel after recording, another after the error |
| Same theme and language | Light on one, dark on another |
| Same day | Evidence from before a deploy |

A panel that cannot reach the shared state stays in; its caption says so.

## Common mistakes

| Mistake | Fix |
|---|---|
| Bug with no source | Label it observed |
| Majority treated as right | Write "differs from the others" |
| Last night's screenshots | Retest, date each figure |
| Easy state captured | Build the matrix first |
| Label hides the marked text | Smaller label or box only |
| Bug without case ID | Add the case that would catch it |

**Red flags, recapture:** "close enough", "same step, different contest", "it was like this yesterday".
