# qa-agent-skills

Tool-agnostic QA skills for coding agents (Claude Code, Cowork, and anything else that reads
`SKILL.md` files).

The core is three skills, covering the situations QA actually shows up in:

| Skill | Use it when | Output |
|---|---|---|
| [`ticket-driven-qa`](skills/ticket-driven-qa) | There **is** a ticket and a code change to verify | A QA ticket, a test run against live environments, one results comment with reproducible bug reports |
| [`exploratory-web-testing`](skills/exploratory-web-testing) | There is **no** spec — just a URL | An observed-behaviour spec → test cases → Qase-importable CSV |
| [`casely`](skills/casely) | There **is** a spec, user story, or acceptance criteria — and you want test cases from it | Review-ready test cases, a TestRail/Qase/Zephyr-ready export, and a Postman collection when the spec describes an API |

Plus seven more:

| Skill | What it does |
|---|---|
| [`qa-automation`](skills/qa-automation) | Principal-SDET partner for Playwright automation: requirements analysis, web/api/mobile monorepo layout with a shared core, flat POMs, `APIRequestContext`, test plans, production-readiness review |
| [`playwright-robot`](skills/playwright-robot) | Turns raw requirements into a Playwright suite by inspecting the live accessibility tree through the Playwright MCP, then self-heals failures |
| [`technical-blogger`](skills/technical-blogger) | Writes and edits technical blog posts, deep-dives, investigations, and SOPs — knowledge representation and evidence hierarchy over storytelling |
| [`technical-blogger-reviewer`](skills/technical-blogger-reviewer) | Reviews a drafted article before publish — hunts Indonesian literal-translation calques ("rancu"), keeps technical terms in English, cuts wordiness, re-verifies claims, and returns the fixed draft plus a review log |
| [`viral-ugc-ads`](skills/viral-ugc-ads) | Short-form video ad scripts (TikTok, Reels, Shorts) tuned for Google Flow / Veo 3 |
| [`repo-gap-audit`](skills/repo-gap-audit) | Answers "what's missing in this repo?": five scanners (unfinished work, dead ends, recent-commit loose ends, resilience, test gaps), a noise filter, ICE-ranked top five with `path:line` evidence, and grounded feature suggestions. Report only, no code changes |
| [`ui-tour`](skills/ui-tour) | Before you change a screen: real screenshots of its key states with numbered pins, every control and its choices, the rough edges ranked, and a map of the source files, as one HTML page |

Nothing here is tied to a company, a product, or a specific tracker. Ticket and code-review
platforms are handled by swappable adapters, and project specifics live in one file you fill in.

## Install

As a Claude Code plugin marketplace:

```
/plugin marketplace add randykaskuser/qa-agent-skills
/plugin install qa-agent-skills
```

Or just clone it and point your agent at the `skills/` folder.

## Why the core three exist

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

## casely

A **Virtual QA Lead**: hand it a requirements document (PDF, DOCX, XLSX, TXT, MD, or pasted
text) and it produces a style guide, a test plan with one approval gate, atomic test cases, and
an Excel export ready for TestRail/Qase/Zephyr import. When the requirements describe an API,
it also builds a ready-to-run Postman collection.

`casely` is a vendored, lightly modified copy of [Casely](https://github.com/JohnWayneeee/casely-qa-skill)
by John Wayne (MIT). See [`skills/casely/NOTICE.md`](skills/casely/NOTICE.md) for exactly what
changed and how to diff against upstream.

## How the three fit together

```
Have a ticket + a diff?             → ticket-driven-qa
Have a spec but no test cases?      → casely
Have nothing but a URL?             → exploratory-web-testing → (Phase 4) casely → Qase CSV
Have cases, want them automated?    → qa-automation (architecture + review) or playwright-robot (generate + self-heal)
About to change a screen?           → ui-tour (see it, its controls and its rough edges first)
Wondering what the repo is missing?  → repo-gap-audit (ranked gaps + feature ideas, no edits)
```

`exploratory-web-testing` writes the observed-behaviour spec that `casely` then turns into a
suite. `ticket-driven-qa` stands alone: it verifies one change end to end and files bugs.

## repo-gap-audit

```
Scope + orient (README, docs, routes: what does it promise?)
   → 5 scanners: unfinished business · dead ends & UX friction · recent momentum (git log)
                 · blind spots & resilience · test & QA gaps
   → reject noise (rubric + "who cares?", "grounded?", "owner reaction" tests)
   → ICE score + S/M/L effort → top five, 2-3 feature suggestions, one "start here"
```

Read-only: it never edits the project. Every finding must cite a `path:line` the agent read, and
"nothing high-leverage here" is an allowed answer. Replies in the user's language.

### Test prompts

The prompts in `skills/repo-gap-audit/evals/evals.json`, each run once with and once without the
skill on three real repos (a Three.js game, an Astro/Svelte multi-tenant player, a FastAPI video
backend scoped to `backend/`):

| # | Prompt | What it checks |
|---|---|---|
| 1 | "apa yang kurang ya di repo lastwar ini? kasih saran fitur juga." | Indonesian phrasing, whole repo, feature suggestions |
| 2 | "Do a gap analysis of players-revamp - what's half-built or broken, and what should we build next?" | Large repo with stale docs, recent-commit loose ends |
| 3 | "what's missing in the backend/ folder of Clipper? mostly care about reliability and tests" | Scope limit and a category focus |

First iteration: 100% of checks passed with the skill against 33% without, at about the same time
(~5 minutes a run). Without the skill every report was a long unranked list (12-30 items) with
partial evidence; with it, each gave a ranked top five with line-level evidence. The skill runs
also found bugs the baselines missed: a write endpoint with no rate limit, Defense progress lost on
tab close, cancelled jobs that cannot be resumed, and an LLM JSON parser reporting wrong-shaped data
as success.

## ui-tour

```
Project notes (.claude/ui-tour.md) → read the screen's code → open it with real data
   → 2-4 key states (+ a phone view for public pages) → pins, controls, rough edges, code map
   → scripts/build_tour.py → one self-contained HTML page → clean up, update the notes
```

Works on any web app, and on the web part of an Electron app. Project specifics (how to start
the app, which record to open, processes never to kill) live in `.claude/ui-tour.md`; copy
`skills/ui-tour/references/project-notes.template.md` there, or let the first tour write it.

```bash
python skills/ui-tour/scripts/build_tour.py tour.json screen-tour.html
```

The spec format is in `SKILL.md`. Images are embedded, so the page is one file you can send.
Cropping needs Pillow; without it the full screenshots are embedded and the pins still line up.

### Test prompts

The prompts in `skills/ui-tour/evals/evals.json`, each run once with and once without the skill
on a real Next.js + FastAPI app:

| # | Prompt | What it checks |
|---|---|---|
| 1 | "I want to redesign Settings → Output in ViralClipper. Show me what it looks like now and what's on it." | A settings screen with a backend; controls table and rough edges |
| 2 | "make me an overview i can look at of the homepage, the AI status card and the job list. layout + where the code is" | Casual phrasing, two areas on one page, a control that must not be clicked |
| 3 | "Give me a visual walkthrough of the install guide page in cloud/install-guide/ before I rework it." | A static page with no app servers, and a phone-width view |

First iteration: 96% of checks passed with the skill against 53% without. Every run with the skill
produced the annotated page and 3-4 measured rough edges; no run without it did either, and one
baseline invented UI options the code does not have. The skill takes about twice as long (around
11 minutes against 6).

## Attribution

- `ticket-driven-qa`, `exploratory-web-testing`, `qa-automation`, `playwright-robot`,
  `technical-blogger`, `technical-blogger-reviewer`, `viral-ugc-ads`, `ui-tour`, `repo-gap-audit` — Randy Maulana, MIT.
- `casely` — John Wayne, MIT, <https://github.com/JohnWayneeee/casely-qa-skill>. Vendored with
  its license intact; modifications listed in `skills/casely/NOTICE.md`.

## License

MIT — see [LICENSE](LICENSE).
