---
name: exploratory-web-testing
description: >
  Explore a live web application in the browser when there is no specification, record what it
  actually does as a testable observed-behaviour spec, and hand that to Casely for a test suite.
  Use whenever the user names a URL or an app and wants testing without providing requirements —
  "test this site", "explore this app", "no spec, just poke at it", "what should we test here?",
  "reverse-engineer the requirements", "cover this page with regression tests" — or when a
  Casely run stalls because no requirements document exists. Also use for exporting existing test
  cases to Qase, which needs its own exact CSV headers rather than a team's column names. Assumes
  a browser is available and drives it directly. Triggers on non-English phrasing too.
license: "MIT"
---

# Exploratory Web Testing

Turn a running web app into a testable spec, then into test cases. This skill covers the part
Casely cannot do: producing requirements when nobody wrote any. Casely still does the test
design and the style matching — this skill feeds it.

## The rule that matters most

**Observed behaviour is not intended behaviour.** With no spec, every bug looks like a feature.
If you write down "clicking Save twice creates two records" as expected behaviour and hand it to
Casely, you have just locked a duplicate-submission bug into the regression suite, and every
future run will assert the bug still works.

So everything observed goes into one of three buckets, and the bucket is never guessed silently:

| Bucket | Meaning | Becomes |
|--------|---------|---------|
| **Confirmed** | Behaviour that is obviously intended — it matches the visible purpose of the control | A test case |
| **Question** | Behaviour that might be intended or might be a defect; you cannot tell without a human | Asked, not assumed |
| **Anomaly** | Behaviour that is almost certainly wrong — console error, broken layout, data loss, silent failure | Reported, never a test case |

A run that produces zero questions has almost certainly mislabelled some. Say so rather than
presenting false confidence.

---

## Phase 0 — Rules of engagement (always ask, never assume)

Before touching the app, establish and state back:

1. **Environment.** Staging or production? On production, stay read-only: no form submissions,
   no sign-ups, no writes, no destructive actions. Ask rather than infer from the hostname.
2. **Authentication.** If the app needs a login, the user signs in themselves in the browser.
   Never ask for credentials in chat and never type them into a page.
3. **Scope and timebox.** Which area, and how long a session. Exploration is unbounded by
   nature; a stated timebox ("30 minutes on the player") is what makes it finishable.
4. **Destructive latitude.** On staging, confirm explicitly that invalid input, boundary values
   and error paths may be exercised. That is where the value is, but it writes data.

State the rules back in one line before starting, so a wrong assumption is caught before it
costs anything.

## Phase 1 — Recon

Load the target and build an inventory before probing anything. Read
`references/exploration-method.md` before this phase.

1. Open the page and read its structure — not a screenshot. Prefer the text/DOM reading tools;
   take screenshots only when layout or rendering is the actual question.
2. Record: routes reachable from here, interactive controls (buttons, inputs, links, media
   players), visible states, and anything that looks stateful (auth, cart, playback, filters).
3. Watch the network and console while the page loads. Endpoints seen here are the API surface
   the spec will describe, and console errors on a clean load are findings in their own right.
4. Produce a short inventory and **show it to the user before probing**. This is the cheapest
   moment to hear "ignore the footer, that's a shared component."

Do not start clicking during recon. Mapping first is what keeps the session from becoming a
random walk.

## Phase 2 — Probe (timeboxed)

Work the inventory using the heuristics in `references/exploration-method.md` — structure,
function, data, platform, operations, boundaries, interruptions. For each control:

1. Exercise the intended path first, and record the observed result precisely — the actual
   text, the actual state change, the actual request. "It works" is not an observation.
2. Then push it: empty, maximum length, wrong type, wrong order, twice quickly, back button
   mid-flow, offline, reload mid-state. Only on staging, or only read-only paths on production.
3. Record every result into the three buckets above as you go. Do not batch this to the end —
   details evaporate, and a half-remembered repro is worthless.
4. Note the request/response for anything API-backed. It is what makes an API-level case
   possible later instead of a UI-only one.

Stop at the timebox even mid-thread. Say what was left unprobed; an honest coverage boundary is
more useful than a padded one.

## Phase 3 — Write the observed-behaviour spec

This is the handoff artifact and the point of the whole session. Follow
`references/observed-spec-format.md` exactly — Casely reads it as if it were a requirements
document, so its structure has to survive that.

Write it to `observed_spec.md`. It must contain, per area: what the feature appears to do, the
observed behaviours as numbered requirement-shaped statements with stable IDs (`OBS-001`), the
data and states involved, the API calls behind it, and separate clearly-marked sections for
open questions and anomalies.

**Show the questions and anomalies to the user and wait.** Their answers change which observed
behaviours are safe to turn into test cases. Going straight to case generation with unresolved
questions is how bugs get canonised.

## Phase 4 — Hand off to Casely

> Casely is bundled in this repo as `skills/casely` (a vendored copy of
> <https://github.com/JohnWayneeee/casely-qa-skill>, MIT, by John Wayne — see its NOTICE.md).
> It turns a requirements document into review-ready test cases and exports. If it is not
> available in your install, this phase degrades gracefully: see the fallback at the end of
> the section.

With `observed_spec.md` settled, invoke the Casely skill exactly as if the user had attached a
requirements document. Casely's own flow takes over: style guide, test plan with an approval
gate, generated cases, export.

Two things to pass along explicitly:

- **The spec is reverse-engineered**, so its "requirements" are observations. Casely's gap
  analysis should treat missing error-path definitions as genuinely undefined, not as spec
  omissions to flag back — they were never written down by anyone.
- **The style example.** For Qase, the example test case file should be a real Qase CSV export,
  not the team's internal format. See the next phase for why.

If Casely is not installed, generate the cases directly using the same discipline — atomic,
independent, deterministic expected results — but say that the dedicated skill would do it
better.

## Phase 5 — Export to Qase

Qase's CSV importer reads the first row to decide what each column is and **will not guess** a
renamed, missing, or reordered header. This is the opposite of Casely's "preserve the team's
exact headers" rule, and the two only agree when the team's format already is the Qase format.

Run the bundled converter over Casely's `results/` folder:

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/exploratory-web-testing/scripts/to_qase_csv.py \
  results qase_import.csv --suite "Client / Area"
```

Useful flags:

- `--template real_qase_export.csv` — takes the header row verbatim from an actual export of the
  user's workspace. **Prefer this whenever the user can supply one**, since it picks up custom
  fields and their Qase version's step format, which no hardcoded list can.
- `--map "Schritte=steps_actions,Priorität=priority"` — for columns the alias table misses.
- `--suite "Parent / Child"` — emits the suite rows first, which Qase requires before cases can
  reference them.

The converter refuses the whole file if any case is malformed, and reports which file and why.
Never describe a partial export as complete. Warnings about dropped columns matter: a column
with no Qase equivalent silently disappears from the import unless a custom field is created
first.

Details of the format, the allowed values, and what is inferred versus documented are in
`references/qase-csv.md`.

---

## Guidelines

### Read the page, don't look at it
Text and DOM reading gives the actual content and structure; a screenshot gives pixels of one
viewport. Screenshot when rendering, layout, or visual state is the thing under test — not as
the default way to see a page.

### One approval gate before probing, one before cases
Phase 1's inventory and Phase 3's questions are the two moments the user's input changes the
outcome. Everything else runs without asking. Do not manufacture extra confirmations, and do not
skip these two.

### Evidence, not impressions
Every recorded behaviour carries what was actually seen: the literal message text, the status
code, the state before and after. A finding a developer cannot reproduce from the notes is not
a finding yet.

### Coverage honesty
Say what was not explored and why — out of timebox, needed a login, would have written data on
production. An exploratory session's value collapses if its boundaries are implied rather than
stated.

### Respect the environment
Production means read-only, every time, regardless of how interesting the untested path looks.
If a valuable check needs writes, name it as something to run on staging instead of doing it.

## Skill files

- `references/exploration-method.md` — heuristics for what to probe and how to record it.
- `references/observed-spec-format.md` — the exact structure of `observed_spec.md`.
- `references/qase-csv.md` — Qase's CSV columns, allowed values, and the converter's behaviour.
- `scripts/to_qase_csv.py` — Casely Markdown cases to Qase-importable CSV.
