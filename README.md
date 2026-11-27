# qa-agent-skills

Tool-agnostic QA skills for coding agents (Claude Code, Cowork, and anything else that reads
`SKILL.md` files).

The core is five skills, covering the situations QA actually shows up in:

| Skill | Use it when | Output |
|---|---|---|
| [`test-a-ticket`](skills/test-a-ticket) | There **is** a ticket and a code change to verify | A QA ticket, a test run against live environments, one results comment with reproducible bug reports |
| [`explore-app-without-spec`](skills/explore-app-without-spec) | There is **no** spec — just a URL | An observed-behaviour spec → test cases → Qase-importable CSV |
| [`verify-bug-fix`](skills/verify-bug-fix) | A reported bug is marked **fixed** and needs retesting | One verdict per ticket: a before/after PNG with a one-line "QA passed" comment, or a repro card and a proposal to reopen |
| [`consistency-check`](skills/consistency-check) | The same flow must match across web, Android, iOS or builds, or the steps of one app must share one layout | Marked side-by-side screenshots judged against a named source of truth, then bugs per platform |
| [`write-test-cases`](skills/write-test-cases) | There **is** a spec, user story, or acceptance criteria — and you want test cases from it | Review-ready test cases, a TestRail/Qase/Zephyr-ready export, and a Postman collection when the spec describes an API |

Plus eleven more:

| Skill | What it does |
|---|---|
| [`report-test-results`](skills/report-test-results) | One easy-to-read results page for a test run: verdict, what it was judged against, every item, the proof for each failure, what is open. For a verified bug fix, before/after tables per ticket plus a PNG to paste into the tracker comment. Called by `test-a-ticket`, `explore-app-without-spec`, `consistency-check` and `verify-bug-fix`; refuses a spec with a failure that has no source, date or proof |
| [`export-cases-to-qase`](skills/export-cases-to-qase) | Markdown test cases (from `write-test-cases` or `explore-app-without-spec`) to one CSV Qase imports: Qase's own headers or a real export as template, suites first, every dropped column named |
| [`automate-ticket-in-batches`](skills/automate-ticket-in-batches) | Autonomous iterative test-automation loop across navigation sections: live visual inspection, catalogue gap analysis, 100% P0/P1 coverage, 1 MR per section, subagent code review, live execution, zero leftovers, and Linear reporting |
| [`automation-architecture`](skills/automation-architecture) | Principal-SDET partner for Playwright automation: requirements analysis, web/api/mobile monorepo layout with a shared core, flat POMs, `APIRequestContext`, test plans, production-readiness review |
| [`write-playwright-tests`](skills/write-playwright-tests) | Turns raw requirements into a Playwright suite by inspecting the live accessibility tree through the Playwright MCP, then self-heals failures |
| [`write-tech-article`](skills/write-tech-article) | Writes and edits technical blog posts, deep-dives, investigations, and SOPs — knowledge representation and evidence hierarchy over storytelling |
| [`review-tech-article`](skills/review-tech-article) | Reviews a drafted article before publish — hunts Indonesian literal-translation calques ("rancu"), keeps technical terms in English, cuts wordiness, re-verifies claims, and returns the fixed draft plus a review log |
| [`write-ugc-video-ad`](skills/write-ugc-video-ad) | Short-form video ad scripts (TikTok, Reels, Shorts) tuned for Google Flow / Veo 3 |
| [`find-repo-gaps`](skills/find-repo-gaps) | Answers "what's missing in this repo?": five scanners (unfinished work, dead ends, recent-commit loose ends, resilience, test gaps), a noise filter, ICE-ranked top five with `path:line` evidence, and grounded feature suggestions. Report only, no code changes |
| [`annotate-screen`](skills/annotate-screen) | Before you change a screen: real screenshots of its key states with numbered pins, every control and its choices, the rough edges ranked, and a map of the source files, as one HTML page |
| [`design-tests-for-new-app`](skills/design-tests-for-new-app) | A new app version or big feature set, from tickets to test design: today-vs-new comparison with a four-bucket case split, strategy and test plan, catalogue cases traced to ticket lines, fresh AC and edge-case reviewer passes, one blocked conflict ticket, one edited-in-place comment per ticket, a coverage page, and cases marked for automation. Resumes or repairs an earlier pass instead of redoing it |

Nothing here is tied to a company, a product, or a specific tracker. Ticket and code-review
platforms are handled by swappable adapters, and project specifics live in one file you fill in.

## Install

As a Claude Code plugin marketplace:

```
/plugin marketplace add randykaskuser/qa-agent-skills
/plugin install qa-agent-skills
```

Or just clone it and point your agent at the `skills/` folder.

## Why the core skills exist

**Most QA bugs are not missed checks. They are checks done in the wrong place.**

A change lands in an admin panel, a CMS, a dashboard. It is easy to test that form until it
shines and never look at the page where a user would actually see the result. `test-a-ticket`
is built around one rule that fixes this:

> Every source check gets at least one consumer check, or is marked **blocked** with a reason.

The second rule is about the other half of wasted QA time — false alarms:

> Isolate before you call it a bug. Use a control record, change one variable at a time, and
> re-check your own last action.

And the third, in `explore-app-without-spec`:

> Observed behaviour is not intended behaviour. Findings are bucketed as confirmed, question,
> or anomaly — only confirmed ones become test cases, so a defect never gets locked into the
> regression suite as an expected result.

## test-a-ticket

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
`skills/test-a-ticket/references/environment-map.template.md` to `.claude/qa-environment-map.md` in your project and fill
it in — environments, IDs, endpoints, share-link format, and the gotchas that cost you an hour
the first time. That file is the whole project-specific surface area. Don't put secrets in it.

Also included: `references/standard-checks.md` (rendered content, rich text and XSS, edge data,
image uploads, save flows, dirty state), `references/browser-techniques.md`, and
`scripts/browser-helpers.js` — a paste-in console helper giving you a request log, forced request
failures, artificial delays, generated test images of any size, file-input injection, rich-HTML
paste, an og-tag checker that verifies the image actually loads, and a toast watcher.

## explore-app-without-spec

```
Rules of engagement → Recon (inventory, shown to you)
   → Probe (timeboxed, seven dimensions)
   → observed_spec.md  (confirmed / questions / anomalies)
   → test cases → qase_import.csv
```

### Qase export (`export-cases-to-qase`)

```bash
python skills/export-cases-to-qase/scripts/to_qase_csv.py \
  results qase_import.csv --suite "Client / Area"
```

Qase's importer will not remap headers, so the converter emits Qase's own column names. Pass
`--template <a real Qase export>` to take the header row from your own workspace instead — that
picks up custom fields and your Qase version's step format. Pure standard library, no
dependencies, no network calls.

## write-test-cases (Casely)

A **Virtual QA Lead**: hand it a requirements document (PDF, DOCX, XLSX, TXT, MD, or pasted
text) and it produces a style guide, a test plan with one approval gate, atomic test cases, and
an Excel export ready for TestRail/Qase/Zephyr import. When the requirements describe an API,
it also builds a ready-to-run Postman collection.

`write-test-cases` is a vendored, lightly modified copy of [Casely](https://github.com/JohnWayneeee/casely-qa-skill)
by John Wayne (MIT). See [`skills/write-test-cases/NOTICE.md`](skills/write-test-cases/NOTICE.md) for exactly what
changed and how to diff against upstream.

## How they fit together

```
Have a ticket + a diff?             → test-a-ticket
Bug marked fixed, needs a retest?   → verify-bug-fix → report-test-results (before/after PNG)
Have a spec but no test cases?      → write-test-cases
Have nothing but a URL?             → explore-app-without-spec → write-test-cases → export-cases-to-qase
Test design done, cases marked?     → design-tests-for-new-app → automate-ticket-in-batches
Have cases, want them automated?    → automation-architecture (architecture + review) or write-playwright-tests (generate + self-heal)
Same flow on several platforms, or steps that should look alike? → consistency-check (what differs, judged against a named source)
Results someone else must trust?    → report-test-results (called by the testing skills; one page: verdict, every item, proof)
About to change a screen?           → annotate-screen (see it, its controls and its rough edges first)
Writing a technical article?        → write-tech-article → review-tech-article
Wondering what the repo is missing?  → find-repo-gaps (ranked gaps + feature ideas, no edits)
```

`explore-app-without-spec` writes the observed-behaviour spec that `write-test-cases` then turns into a
suite. `test-a-ticket` stands alone: it verifies one change end to end and files bugs.

## find-repo-gaps

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

The prompts in `skills/find-repo-gaps/evals/evals.json`, each run once with and once without the
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

## annotate-screen

```
Project notes (.claude/ui-tour.md) → read the screen's code → open it with real data
   → 2-4 key states (+ a phone view for public pages) → pins, controls, rough edges, code map
   → scripts/build_tour.py → one self-contained HTML page → clean up, update the notes
```

Works on any web app, and on the web part of an Electron app. Project specifics (how to start
the app, which record to open, processes never to kill) live in `.claude/ui-tour.md`; copy
`skills/annotate-screen/references/project-notes.template.md` there, or let the first tour write it.

```bash
python skills/annotate-screen/scripts/build_tour.py tour.json screen-tour.html
```

The spec format is in `SKILL.md`. Images are embedded, so the page is one file you can send.
Cropping needs Pillow; without it the full screenshots are embedded and the pins still line up.

### Test prompts

The prompts in `skills/annotate-screen/evals/evals.json`, each run once with and once without the skill
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

- `test-a-ticket`, `explore-app-without-spec`, `automation-architecture`, `write-playwright-tests`,
  `write-tech-article`, `review-tech-article`, `write-ugc-video-ad`, `annotate-screen`, `find-repo-gaps`,
  `automate-ticket-in-batches`, `design-tests-for-new-app`, `consistency-check`, `report-test-results`, `verify-bug-fix` — Randy Maulana, MIT.
- `write-test-cases` — John Wayne, MIT, <https://github.com/JohnWayneeee/casely-qa-skill>. Vendored with
  its license intact; modifications listed in `skills/write-test-cases/NOTICE.md`.

## License

MIT — see [LICENSE](LICENSE).
