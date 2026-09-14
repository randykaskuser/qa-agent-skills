# qa-agent-skills

Tool-agnostic QA skills for coding agents (Claude Code, Cowork, and anything else that reads
`SKILL.md` files).

Two skills, for the two situations QA actually shows up in:

| Skill | Use it when | Output |
|---|---|---|
| [`ticket-driven-qa`](skills/ticket-driven-qa) | There **is** a ticket and a code change to verify | A QA ticket, a test run against live environments, one results comment with reproducible bug reports |
| [`exploratory-web-testing`](skills/exploratory-web-testing) | There is **no** spec — just a URL | An observed-behaviour spec → test cases → Qase-importable CSV |

Nothing here is tied to a company, a product, or a specific tracker. Ticket and code-review
platforms are handled by swappable adapters, and project specifics live in one file you fill in.

## Install

As a Claude Code plugin marketplace:

```
/plugin marketplace add randykaskuser/qa-agent-skills
/plugin install qa-agent-skills
```

Or just clone it and point your agent at the `skills/` folder.

## Why these two skills exist

**Most QA bugs are not missed checks. They are checks done in the wrong place.**

A change lands in an admin panel, a CMS, a dashboard. It is easy to test that form until it
shines and never look at the page where a user would actually see the result. `ticket-driven-qa`
is built around one rule that fixes this:

> Every source check gets at least one consumer check, or is marked **blocked** with a reason.

The second rule is about the other half of wasted QA time — false alarms:

> Isolate before you call it a bug. Use a control record, change one variable at a time, and
> re-check your own last action.

And the third, in `exploratory-web-testing`:

> Observed behaviour is not intended behaviour. Findings are bucketed as confirmed, question,
> or anomaly — only confirmed ones become test cases, so a defect never gets locked into the
> regression suite as an expected result.

## ticket-driven-qa

```
Plan: ticket + MR/PR diffs → what is actually deployed → the change → surfaces map → QA ticket
Run:  one permission question → QA test data → test the source AND every consumer
      (public page, navigation, share links + og tags, public API, other tenants)
      → isolate before calling a bug → results comment + ticked checkboxes
      → proposed bug tickets (created only after approval) → clean up
```

Every bug gets a **repro card**: exact URL, test-data ID, numbered steps, expected vs actual as
literal text or status code, evidence (screenshot + request/response), and whether production is
affected. A bug report with only a description is not accepted by this skill.

**Adapters** — the workflow never names a tool; these map it onto real ones:

- `references/adapters/issue-trackers.md` — Linear, Jira, GitHub Issues
- `references/adapters/code-review.md` — GitLab, GitHub, Bitbucket, local clone
- `references/adapters/test-management.md` — Qase, TestRail, Zephyr (optional)

**Setting it up for your project:** copy
`skills/ticket-driven-qa/references/environment-map.template.md` to `environment-map.md` and fill
it in — environments, IDs, endpoints, share-link format, and the gotchas that cost you an hour
the first time. That file is the whole project-specific surface area. Don't put secrets in it.

Also included: `references/standard-checks.md` (rendered content, rich text and XSS, edge data,
image uploads, save flows, dirty state), `references/browser-techniques.md`, and
`scripts/browser-helpers.js` — a paste-in console helper giving you a request log, forced request
failures, artificial delays, generated test images of any size, file-input injection, rich-HTML
paste, an og-tag checker that verifies the image actually loads, and a toast watcher.

## exploratory-web-testing

```
Rules of engagement → Recon (inventory, shown to you)
   → Probe (timeboxed, seven dimensions)
   → observed_spec.md  (confirmed / questions / anomalies)
   → test cases → qase_import.csv
```

### Qase export

```bash
python skills/exploratory-web-testing/scripts/to_qase_csv.py \
  results qase_import.csv --suite "Client / Area"
```

Qase's importer will not remap headers, so the converter emits Qase's own column names. Pass
`--template <a real Qase export>` to take the header row from your own workspace instead — that
picks up custom fields and your Qase version's step format. Pure standard library, no
dependencies, no network calls.

## Companion skill (not included)

Phase 4 of `exploratory-web-testing` hands the observed spec to **Casely**, a separate MIT-licensed
plugin by John Wayne that turns requirements into review-ready test cases, TestRail/Qase exports,
and Postman collections: <https://github.com/JohnWayneeee/casely-qa-skill>

It is not vendored here so it keeps getting upstream updates. Both skills work without it — case
generation is just weaker.

## License

MIT — see [LICENSE](LICENSE).
