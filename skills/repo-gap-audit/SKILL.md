---
name: repo-gap-audit
description: >
  Audit a codebase for what is missing, half-built, or quietly broken, and suggest the features it
  should have next — a ranked, evidence-backed report (every finding has a file:line), not a code
  change. Use whenever someone asks what a repo lacks or what to improve: "what's missing in this
  repo?", "apa yang kurang di repo ini?", "gap analysis", "audit this codebase", "what should we
  build or fix next?", "find the weak spots", "kasih saran fitur", "where are the loose ends?", or
  points at a project and asks for improvement ideas — even if they never say "audit". Covers
  TODO/stub/placeholder scans, dead-end user flows, missing feedback and error states, loose ends
  from recent commits, swallowed errors, and missing tests. Not for reviewing one diff or PR (use a
  code-review skill), verifying a ticket (ticket-driven-qa), or exploring a live URL with no code
  (exploratory-web-testing). Triggers on non-English phrasing too.
license: "MIT"
---

# Repo Gap Audit

Answer "what is missing here?" with findings someone would actually act on. The deliverable is a
report: a ranked shortlist of gaps, a few grounded feature suggestions, and one place to start.
This skill does not change code. Fixing is a separate decision the owner makes after reading.

The hard part is not finding things. Any repo has hundreds of TODOs and nits. The hard part is
throwing away the noise so the five items left are ones the owner reads and says "yes, that is
obviously missing". A report padded with padding tweaks and renamed variables teaches the reader
to ignore the next one.

## Ground rules

- **Read-only.** Read files, grep, run `git log`, list routes. Do not edit project files, commit,
  install, or run anything that writes or calls external services. The only file you may write is
  the report itself (see Finish). Running an existing fast test or lint command is
  fine if it helps confirm a finding; skip it if it needs setup or takes minutes.
- **Every finding needs evidence**: a `path:line` (or line range) you actually read. A finding you
  cannot point at is a guess, so drop it. Quote the line when it makes the point by itself.
- **Fewer, better.** Five strong findings beat fifteen mixed ones. "Nothing high-leverage found in
  area X" is a valid result and better than inventing something.
- **Reply in the user's language.** Keep code, paths and identifiers as they are.

## Step 1: Scope and orient (a few minutes, not an hour)

Default scope is the whole repo. If the user named a folder, feature, or app inside a monorepo,
stay inside it, and only read outside it to understand how it is used.

Before scanning, build a picture of what the product is supposed to do, because a gap only exists
relative to an intent:

1. Read `README*`, `docs/`, `CHANGELOG*`, and any product or spec files.
2. Read the manifest (`package.json`, `pyproject.toml`, `go.mod`, ...) for the stack and scripts.
3. Find the entry points users touch: routes/pages, CLI commands, API endpoints, screens.
4. Note what the repo *promises* (README features, UI labels, menu items, API docs) versus what it
   *has*. The difference is where the best findings come from.

Write down in two or three lines what the product is and who uses it. You will need it to judge
impact.

## Step 2: Run the five scanners

Run them in order and systematically. Grep first, then read the surrounding code to confirm. A
grep hit is a lead, not a finding. Aim for 5-10 confirmed candidates in total before ranking.

**1. Unfinished business (highest yield).**
- Grep for `TODO`, `FIXME`, `XXX`, `HACK`, `coming soon`, `not implemented`, `placeholder`,
  `lorem`, `stub`, `mock`, `dummy`, `NotImplementedError`, `throw new Error('TODO`, empty handlers
  (`onClick={() => {}}`, `console.log` as the only body), and routes or menu items that render
  nothing.
- Compare README/docs promises to the code: features described but absent, mocked, or behind a
  flag that is always off.
- Skip TODOs in vendored code, generated files, and tests for things that already exist.

**2. Dead ends and UX friction.** Walk the main user journeys in the code as a first-time user would:
- Where does a flow stop with nowhere to go (no back link, no next step, no empty-state action)?
- Where does an action give no feedback: no loading state, no success message, no error shown?
- Which controls are icon-only with no label or `aria-label`? Which interactions are hidden (long
  press, hover-only, keyboard-only) with no hint?
- Which screens have no empty, loading, or error state at all?

**3. Recent momentum.** Run `git log --oneline -n 20` (and `--since="2 weeks ago"` if the history is
busy), then open the two or three most substantial recent commits. Recent work is where loose ends
live: a new field with no validation, a new component not wired in, a new endpoint with no UI or no
test, a migration with no rollback. Skip this scanner if the folder is not a git repo, and say so.

**4. Blind spots and resilience.** Ask what happens when things go wrong:
- Empty, huge, or malformed input; missing config or env vars; corrupt local storage.
- Network or third-party failure: is there a timeout, retry, fallback, or user-visible message?
- Swallowed errors: `catch {}`, `catch (e) {}`, `except: pass`, `.catch(() => {})`, promises with
  no rejection handling, errors logged but the UI left spinning.
- Secrets or credentials committed in the repo (report the path, never print the value).

**5. Test and QA gaps.** This is a QA repo's home ground, so look closely:
- Core flows and endpoints with no test at all; which ones matter most.
- Skipped or disabled tests (`.skip`, `xit`, `@pytest.mark.skip`, `test.fixme`) and why.
- CI config that does not run a suite that exists, or has no test step.
- Tests that assert nothing meaningful (only "renders without crashing", snapshot-only).

## Step 3: Filter with the quality rubric

Test every candidate against this table. Anything in the reject column is out, however easy.

| Category | Reject (noise) | Accept (high leverage) |
|---|---|---|
| UI / UX | Spacing or color tweaks, icon swaps, CSS reformatting, generic dark mode | Removing a dead end, adding missing feedback, labelling cryptic controls, making blank or broken states informative |
| Feature | Unused helpers, speculative abstractions, multi-month rewrites | Finishing a stubbed or broken flow, adding missing core content, wiring an unlinked UI to real state or storage |
| Reliability / Security | Comments, renames, minor type tweaks | Handling unhandled rejections, fixing broken fallbacks, input validation, recovering from corrupt data, removing committed secrets |
| Tests / QA | Raising coverage numbers on trivial code | Covering a core flow that has none, un-skipping a test that hides a real bug, adding the missing CI step |

Then apply three tests. Drop the candidate if it fails any of them:

1. **Who cares?** Would a user or the owner notice the difference within a minute of using the
   product, or would a bug here hurt someone real? If neither, drop it.
2. **Grounded?** Did you read the code that proves it, not just a grep line or a filename?
3. **Owner reaction.** Would the owner read it and say "yes, that is obviously missing", rather than
   "why are you telling me this"? Size is not a reason to drop it here. Report big items too, with
   an honest effort label.

## Step 4: Score and rank

Score each surviving candidate 1-5 on Impact, Confidence, and Ease, and multiply (ICE). Impact is
how much users or the owner gain. Confidence is how sure you are the gap is real and the fix is
right. Ease is the inverse of effort. Also give each an effort label so the reader can plan:
**S** (under 2 hours), **M** (about a day), **L** (several days or more).

Rank by ICE score. Show the top five in the report. Keep the rest in a short "also found" list,
one line each, so nothing found is lost.

## Step 5: Feature suggestions

Gaps are about what is broken or unfinished. Suggestions are about what the product should grow
next. Offer two or three, and ground each one in the repo, not in what products like it usually
have. Good sources:

- Data the app already stores but never shows or lets users act on (a model field with no UI, a
  log with no viewer).
- An endpoint or capability that exists for one entity but not its sibling (export for orders but
  not customers).
- A recurring manual step visible in scripts, docs, or comments ("run this by hand after deploy").
- A README or roadmap item with partial groundwork already in the code.

Each suggestion states the evidence, the user it helps, and an effort label. Skip this section and
say why if nothing is grounded enough.

## Report format

Use this template. Keep it tight: the reader should get the point from the summary and the table
alone.

```markdown
# Gap audit: <repo or area>

**What this is:** <one or two lines: the product and who uses it>
**Scope:** <whole repo | path> · **Commit:** <short sha> · **Scanners run:** <1-5, note any skipped>

## Start here
<One sentence: the single item to do first and the concrete result, e.g. "Wire the Export button in
`src/pages/Report.tsx:88` to the existing `/api/export` endpoint, so users can download reports
instead of hitting a button that does nothing.">

## Top findings

| # | Finding | Category | Effort | ICE |
|---|---|---|---|---|
| 1 | <title> | Feature | S | 60 |
| ... | | | | |

### 1. <title>
- **Evidence:** `path:line` <short quote if it helps>
- **Symptom:** <what is missing, broken, or frustrating today>
- **Impact:** <who suffers, and how>
- **Suggested fix:** <one or two lines, what done looks like>
- **ICE:** Impact <x> × Confidence <y> × Ease <z> = <score>

<repeat for each of the top five>

## Feature suggestions
1. **<name>**: <what it is> · Evidence: `path:line` · Helps: <who> · Effort: <S/M/L>

## Also found
- <one line each, with path:line>

## Not flagged
<One or two lines on what you checked and found fine, or noise you deliberately left out, so the
reader knows the area was looked at.>
```

## Finish

Present the report in the conversation. If it is long, or the user wants to share it, also save it
as `gap-audit.md` in the repo root (or the path they give) and say where it is. Do not commit it.

End with one line offering the next step: fix the "Start here" item, turn the findings into tickets,
or dig deeper into one area. Then stop. The owner decides what happens next.
