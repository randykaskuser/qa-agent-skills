# Templates

Keep every one of these in simple sentences. A developer reading the ticket should not have to
decode anything.

### QA ticket

```markdown
## Goal
<one or two plain sentences: what to test, and what must stay the same>
Dev ticket: <DEV-ID> (<who asked / why>). Related: <other ticket IDs + their status>.

## Test URLs
- Source (test env): <url>
- Consumer (public page / share page / API): <url(s)>

## What changed (from the code)
**<repo> !<MR/PR number>** (merged to `<branch>`)
- <behaviour, exact UI strings, endpoints and payloads, limits>

**Already checked on <date>:** <deployment / bundle check results>

## Test data
<records to create, images and values to prepare>

## Test checklist
### A. <Source flow>
- [ ] <one observable check per line — action → expected>
### B. <Legacy / regression>
### C. <Consumer: public page / navigation / share page / API>
### D. <Other surfaces not covered by the change — native apps, other tenants, crawlers>

## Risks to check (from reading the code, not confirmed bugs)
1. **<name>.** <what might go wrong, how to trigger it>

## Done when
- [ ] <sections> pass on <environments>
- [ ] Other surfaces checked, bugs linked to this ticket
```

### Results comment

```markdown
## Test run — <date> (<environments>)
**Result (<N> checklist items): <p> pass · <f> fail · <b> blocked/partial/not run.**
<one-sentence verdict>

**Test data:** <records + IDs + links>. <what was changed on them>.

### 🔴 Critical findings
<only if any — with the full repro card inline>

### Bugs
1. **<title> (<severity>).** <one-line impact> — repro card below / screenshot attached

### Results
**A. <section> (<x>/<y> pass)** — <compact list of what passed, with literal observed values>
<fails and blocked items, each with a reason and the exact command or step the user can run instead>

### Not run / blocked
<item — why — what would unblock it>
```

### Bug repro card

A developer must be able to reproduce from this card alone.

```markdown
**<Title>** — <Severity: Critical/High/Medium/Low> — <introduced by !<MR> | pre-existing> — <also on production: yes/no/unknown>
- **Env / URL:** <exact URL>
- **Test data:** <record name + ID>
- **Steps:**
  1. <exact click / input / value>
  2. …
- **Expected:** <from the ticket or the code>
- **Actual:** <literal text, status code, request body, DOM or CSS value>
- **Evidence:** <screenshot attachment> · <request → response excerpt>
- **Isolation:** <control used, the one variable that triggers it>
- **Likely cause:** <file/line or behaviour — mark clearly as a hypothesis>
```

### Chat escalation draft

Send only after explicit approval, to the channel or person the user names.

```text
Heads-up: <one-line impact> on <environment>. Found while testing <QA-ID> (<DEV-ID>).
Repro: <URL> → <1–2 steps> → <actual>. Expected <expected>.
Affects: <scope, e.g. all share links for every record type>. Details and evidence: <ticket link>
Could you take a look, <owner>? I have not changed anything on production.
```
