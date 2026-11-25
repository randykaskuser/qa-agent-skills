---
name: consistency-check
description: Use when the same flow, screen or feature must look and behave the same across platforms or builds (web, Android, iOS, staging vs production) and you need screenshot proof of what differs. Also use when a comparison table or bug list rests on screenshots that may be stale, taken in different states, or have no stated source of truth.
license: "MIT"
---

# Consistency Check

Compare one flow across platforms with screenshots that are marked, side by side, and judged against a named source of truth.

**Core rule:** a difference is only a bug against a source of truth. Without one, it is "observed".

## Steps

1. **Find the source of truth, per item.** Order: ticket mock or acceptance criteria, then design file, then the majority of platforms, then nothing. Write each rule down with where it came from. "No mock found" is a valid answer; label the item *observed*.
2. **Fix the state matrix before any screenshot.** Rows are the items, columns the platforms. Every cell names the same contest or record, the same step, the same typed input, the same selection, the same theme and language. Fill it in first.
3. **Capture each platform in its cell.** Note build, version, date. Crop to the part that matters.
4. **Mark.** Boxes on the image: red differs from the source, green matches it, amber a different pattern with no source. One short label per box. Never cover the text you mark.
5. **Compare.** One image per item with the platforms side by side and one caption line per platform. Add a table of all items (item, one column per platform, ticket).
6. **Re-verify, then publish.** Retest every claim on the day you publish. A deploy can fix a bug overnight, and a stale figure then calls a fixed platform wrong.
7. **File.** One parent ticket per platform, bugs numbered with Expected, Actual, Steps, the source of truth and the test case ID. Put the proof page link in each. Close a bug when a retest shows it fixed.

`scripts/compare_panels.py` draws the boxes and builds the side-by-side image.

## Check the matrix before publishing

| Check | Fail looks like |
|---|---|
| Same contest or record | One platform shows a 4-checkbox contest, the others 2 |
| Same input state | One panel typed, the others empty |
| Same selection | One answer picked, the others not |
| Same moment in the flow | One panel after recording, another after the error |
| Same theme and language | Light on one, dark on another |
| Same day | Evidence from before a deploy |

A panel that cannot reach the shared state stays in, but the caption says so.

## Common mistakes

| Mistake | Fix |
|---|---|
| Calling a difference a bug with no source | Label it observed |
| Treating the majority as right | Say "differs from the others", not "wrong" |
| Reusing last night's screenshots | Retest, date-stamp each figure |
| Capturing the easy state | Build the matrix first |
| Labels hiding the thing marked | Smaller label, or box without label |
| Bugs without case ID | Add the ID of the case that would catch it |

**Red flags, stop and recapture:** "close enough", "same step, different contest", "it was like this yesterday".
