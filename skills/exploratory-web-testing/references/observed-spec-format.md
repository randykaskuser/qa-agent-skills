# The observed-behaviour spec

`observed_spec.md` is the handoff artifact. Casely reads it as a requirements document, so it
has to look like one: numbered, stable-IDed statements it can plan coverage against and build a
traceability matrix from.

The difference from a real spec is that every statement is an observation, and the document says
so in its own header. That framing is what stops a defect being quietly promoted to expected
behaviour.

## Structure

````markdown
# Observed behaviour — <app / area>

**This is a reverse-engineered spec.** Every statement below describes what the application was
observed to do on <date>, in <environment>, not what it was designed to do. Statements are
testable claims; open questions and anomalies are listed separately and are NOT requirements.

Session: <scope> | Timebox: <duration> | Build/URL: <url>

## 1. <Area name>

**Apparent purpose:** one sentence on what this area seems to be for.

### Observed behaviour

- **OBS-001** — Statement in present tense, one behaviour, testable as written.
- **OBS-002** — ...

### States and data

- States: <e.g. signed out, signed in, playing, paused, error>
- Data involved: <fields, formats, observed limits>
- Discovered limits: <value, and that it was discovered rather than specified>

### API observed

| Method | Path | Trigger | Observed responses |
|--------|------|---------|--------------------|
| GET | /api/stream | page load | 200 with stream url; 404 seen when slug unknown |

## 2. <Next area>

...

---

## Open questions

Numbered, each naming what changes depending on the answer.

- **Q-01** — <observation>. Intended, or a defect? If intended, it needs a test case asserting
  it; if not, it should not be locked into the suite.

## Anomalies

Things that are almost certainly wrong. These become bug reports, never test cases.

- **A-01** — <what happened> | Steps: <numbered> | Expected: <what a reasonable user expects> |
  Evidence: <console line, status code, screenshot>

## Not explored

- <area> — <why: timebox, needed login, would have written data on production>
````

## Rules

**One behaviour per OBS.** "Play starts audio and the button changes and the title updates" is
three statements. Casely writes one case per statement, and a compound statement produces a
compound case, which is exactly what atomicity is meant to prevent.

**Present tense, active, testable.** "The player displays an error message when the stream is
unreachable" — not "we saw an error appear sometimes."

**Stable IDs.** `OBS-001` upward, never renumbered once shared. Casely's traceability matrix
points at these, and renumbering silently breaks every reference.

**No inferred requirements.** If it was not observed, it is not in the observed-behaviour
section. Something that *should* exist but does not — no error handling on a failed request, for
instance — is an open question or an anomaly, not an OBS statement.

**Measurements are not requirements.** An observed 2-second load is a measurement. Only a stated
threshold is a requirement. Where a threshold clearly matters and nobody set one, that is Q-nn.

**Keep the questions visible.** Casely will happily generate cases for every OBS statement. If a
question is unresolved, either resolve it with the user first or mark the affected statements so
the plan can exclude them.

## Handing off

Point Casely at `observed_spec.md` the way a requirements document would be attached, and say:

1. This is reverse-engineered — undefined error paths are genuinely undefined, not spec gaps to
   report back.
2. Which OBS statements are blocked on open questions, so the plan can leave them out.
3. What the style example is. For a Qase workspace, that should be a real Qase CSV export rather
   than the team's internal spreadsheet format.
