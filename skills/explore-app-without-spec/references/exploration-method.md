# Exploration method

How to probe a web app with no spec, and what to write down while doing it.

## The tour heuristic

Cover an app along seven dimensions rather than by clicking around. Each answers a different
question, and skipping one is how whole categories of defect survive to production.

| Dimension | Question | Typical finding |
|-----------|----------|-----------------|
| **Structure** | What is it made of? | Orphaned routes, dead links, components rendered with no data |
| **Function** | What does it do? | A control that does nothing, or two that do the same thing |
| **Data** | What does it operate on? | Boundary and format failures, encoding, empty and huge values |
| **Platform** | What does it depend on? | Browser, viewport, network, autoplay policy, third-party embeds |
| **Operations** | How is it actually used? | Realistic sequences nobody tested — back button, refresh, two tabs |
| **Time** | What changes with it? | Session expiry, timezones, stale caches, race conditions |
| **Interruption** | What if it stops? | Offline, slow network, a failed dependency, a cancelled request |

Work them in that order. Structure and Function build the map; the rest push on it.

## Probing a single control

For each interactive element, in this order:

1. **Intended use.** Do the obvious thing. Record the exact observed result.
2. **Empty.** Submit with nothing. Is the message specific and does focus land usefully?
3. **Boundaries.** One below, at, and one above every limit you can find or infer. Where no
   limit is stated, find where it actually breaks — that discovered limit is a question for the
   team, not a fact about the product.
4. **Wrong type and shape.** Letters in a number field, a 5000-character name, emoji, RTL text,
   leading and trailing spaces, HTML and SQL-looking strings (to check escaping, not to attack).
5. **Repetition and timing.** Double-click submit. Click while the request is in flight. Two
   tabs on the same record.
6. **Navigation.** Back button mid-flow. Refresh mid-state. Deep-link straight into a step.
7. **Interruption.** Go offline and act. Throttle to slow 3G. Watch what the UI claims while the
   request is pending or failed.

Not every control needs all seven. Money, auth, and anything that writes data get all of them.

## What to watch beyond the page

- **Console.** Errors and warnings on a clean load are findings. So is a stack trace that
  appears only on the error path.
- **Network.** Method, path, status, and shape of request and response for each action. This is
  what makes API-level test cases possible later instead of UI-only ones.
- **State after reload.** Whether what you just did survived. Silent non-persistence is common
  and almost never in a spec.
- **What the UI says while waiting.** A button that stays enabled during a request, or a spinner
  that never resolves on failure, is a defect that only interruption testing exposes.

## Recording as you go

One line per observation, written at the moment it happens:

```
[area] action -> observed result | evidence | bucket
```

For example:

```
[player] click play with network offline -> spinner spins indefinitely, no message,
console: "MediaError: src not supported" | screenshot + console line | ANOMALY
```

Three rules:

- **Quote what you saw.** "Shows an error" is not a record. The literal message is.
- **Bucket immediately** — confirmed, question, or anomaly. Deciding later means deciding from
  memory, which is where false confidence enters.
- **Note the state you were in.** Most non-reproducible findings are reproducible once the
  precondition is written down.

## Sizing the session

A timebox is what makes exploration finishable. Rough shape for a single area:

| Time | Realistic depth |
|------|-----------------|
| 15 min | One flow, intended path plus obvious negatives |
| 30–45 min | One area across all seven dimensions |
| 90 min | A module, several flows, with API observation |

Stop at the box even mid-thread, and record what was left open. The unexplored list is a
deliverable, not an admission.

## Turning observations into requirement-shaped statements

Casely needs statements it can plan coverage against. Convert as literally as possible:

- Observation: "clicking play starts audio within ~2s and the button becomes pause"
- Statement: `OBS-012: Activating the play control starts stream playback and the control
  changes to a pause affordance.`

Keep the timing out unless it was stated somewhere; an observed 2 seconds is not a requirement,
it is a measurement. Where a number genuinely matters and nobody specified it, that is a
question, not a statement.
