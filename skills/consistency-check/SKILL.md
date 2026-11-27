---
name: consistency-check
description: Use when the same flow, screen or feature must look and behave the same across platforms or builds (web, Android, iOS, staging vs production), or when the steps, modules or screens of one app must look and behave alike (layout, text, components, states, behaviour), and you need screenshot proof of what differs. Also use when a comparison table or bug list rests on screenshots that may be stale, taken in different states, or have no stated source of truth.
license: "MIT"
---

# Consistency Check

Compare one flow with marked, side-by-side screenshots in two directions: across platforms (the same step on web, Android, iOS) and within each platform (the same element on every step or module).

**Core rule:** a difference is a bug only against a source of truth. Without one it is *observed*, and you propose a standard.

## Steps

1. **Source of truth, per item.** Order: ticket mock or acceptance criteria, design file, majority of platforms, majority of steps on one platform. Open every attachment and linked design before writing "no mock". Name where each rule came from.
2. **State matrix.** Columns are platforms. Rows are each step or module × each state it can reach: default, empty, loading, error, **disabled** (e.g. Save before required fields), success. Every cell uses the same record, input, selection, theme and language. A cell that cannot reach its state stays in, captioned why.
3. **Element checklist.** Record the value in every cell, not "matches":
   - **Layout:** alignment and position against a fixed anchor (close X, back, top edge), spacing, section order.
   - **Text:** wording, case, typography, date and number format.
   - **Components:** buttons (label, style, placement), inputs, icons, colours, tables, filters.
   - **Behaviour:** confirm dialogs, cancel and back, what follows save or delete, keyboard and focus.
4. **Capture** today, after the last deploy. Note build and date; crop to what matters. A figure from another record, step or day is not evidence.
5. **Mark:** red differs from the source, green matches, amber differs with no source. Labels never cover the marked text.
6. **Compare both directions.** Across platforms: one image per step, platforms side by side. Within a platform: one image per platform with its steps side by side, for each element that changes between them. Add a steps × elements × platforms table.
7. **Build the page.** **REQUIRED SUB-SKILL:** qa-agent-skills:report-test-results (run type: platform comparison). `stats`: one entry per platform counting differences, not runs. `rule`: the source of truth used.
8. **Propose, then stop.** Reply with the page link and a list to approve: a proposed standard for each *observed* item (the pattern most steps and platforms already use), one parent ticket per platform with numbered bugs, within-platform ones included (Expected, Actual, Steps, source, test case ID, proof link), and existing bugs the retest shows fixed. Ask which to create or close.
9. **File what was approved,** add the links to the spec and republish to the same URL.

`compare_panels.py` in report-test-results draws the boxes and the side-by-side images.

## Common mistakes

| Mistake | Fix |
|---|---|
| Panels from different records, inputs or moments | Recapture to the matrix |
| Element judged left/centre only | Check its position against the anchor |
| Platforms match each other, own steps disagree | Do the within-platform pass |
| Only default state opened | Fill every state row |
| "No mock" before opening attachments | Open them first |
| Open question, no proposal | Propose the majority pattern |
| Majority treated as right | Write "differs from the others" |
| Bug without case ID | Add the case that would catch it |

**Red flags, recapture:** "close enough", "same step, different contest", "it was like this yesterday".
