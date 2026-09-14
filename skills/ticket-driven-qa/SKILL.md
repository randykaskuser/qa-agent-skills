---
name: ticket-driven-qa
description: Plan and run hands-on QA for a feature or change that already has a ticket and a code change — read the ticket and the merge/pull request diffs, write a QA ticket, then test the surface that was changed AND every surface that consumes it (public UI, navigation, share links and og tags, public API, other tenants or brands), and report results with reproducible bug evidence back to the tracker. Use whenever someone gets an ad-hoc test task — "create a testing ticket for ABC-123", "test this MR", "run what you can from this ticket", "verify this change on staging", a ticket link plus a merge-request link, or an admin URL plus a public URL — even if they don't say "QA ticket". Not for exploring an app with no ticket or spec (use exploratory-web-testing for that).
---

# Ticket-driven QA

Turn a change (a ticket plus its merge/pull requests) into a grounded QA ticket, execute it against live test environments, and report results a developer can act on without asking a single follow-up question.

This skill is tool-agnostic. The workflow below never names a specific tracker or forge. Read the matching adapter in `references/adapters/` for the concrete API calls:

- `references/adapters/issue-trackers.md` — Linear, Jira, GitHub Issues
- `references/adapters/code-review.md` — GitLab, GitHub, Bitbucket
- `references/adapters/test-management.md` — Qase, TestRail, Zephyr (optional)

## The idea that matters most

**A change to an admin or source surface is not verified until its effect is seen where users see it.** The place you edit is only the *source*. Every write there has *consumers*: the public page, the navigation menu, share pages and their og tags, the public API that mobile apps read, other tenants or brands running a different build, and crawlers. The easiest mistake is to test the form thoroughly and never look at the result. So **every source check gets at least one consumer check, or is marked blocked with the reason.**

The second idea: **isolate before you call it a bug.** Most false alarms come from a neighbouring feature, a mis-aimed click, or pre-existing behaviour. Before reporting, change one variable, use a control record, and re-check your own last action.

## Modes

Decide from the request. When both are asked for, run them in sequence.

- **Plan**: "create a testing ticket", "what should we test". Phases 1–4, ending with a QA ticket in the tracker.
- **Run**: "test this", "run what you can from ABC-123". Phases 5–9 against an existing QA ticket. If there is no QA ticket yet, do Plan first — its checklist is the thing that gets executed.

Load task-tracking and user-messaging tools at the start. A run has many steps and the user may walk away.

Read `references/environment-map.md` before Phase 1 if the project has one. If it doesn't, copy `references/environment-map.template.md`, fill it in during Phase 1, and keep it current — it is the single biggest time saver on later runs.

---

## Phase 1: Gather

1. **Ticket.**
   - Read the dev ticket(s) *with their relations*. Acceptance criteria, "what to consider" lists and linked backend/frontend tickets are all test input.
   - Also run a keyword search on a distinctive term from the change (for example `og:image`). Related work is often *mentioned* but not linked, and a keyword search finds it.
   - Note each related ticket's status. A dependency still in "Todo" means its checks can only be *noted*, not failed.
2. **Code.**
   - Read both the MR/PR **description** and the **diffs**, skipping lockfiles.
   - Record the **target branch**. A change merged to a shared integration branch is not the same as "live for every tenant".
   - If the agent sandbox cannot reach the forge, drive it through the user's logged-in browser and call the forge REST API from the page context. See `references/adapters/code-review.md`.
   - Never solve a CAPTCHA or bot check yourself. Ask the user to click it.
3. **Internal docs** (optional, read-only). If a wiki or docs tool is connected, search for the feature or environment docs. Skip silently if it isn't.
4. **What is actually deployed.** Don't assume a merged MR is live. Search the deployed JS for a string unique to the change — a new UI label, a CSS class, a field name — from a page on that origin:
   ```js
   const urls = [...new Set(performance.getEntriesByType('resource')
     .map(e => e.name).filter(u => u.startsWith(location.origin) && u.endsWith('.js')))];
   const hits = [];
   for (const u of urls) { const t = await fetch(u).then(r => r.text()); if (t.includes('<NEW UI STRING>')) hits.push(u); }
   hits
   ```
   Route chunks load lazily. If nothing matches, open the relevant page first, or crawl imports from the entry file. On a logged-out site, fetch the entry bundle and scan the route chunks it lists. Then open the page and confirm the feature is visible in the DOM.
5. **Which backend an environment talks to.** Read `performance.getEntriesByType('resource')` on the page. The API host tells you which backend you are really testing — this catches "I was on staging UI but production data" before it wastes an hour.

## Phase 2: Understand the change from the code

Write down, in plain sentences:

- **What changed.** The behaviours, the exact UI strings, the endpoints and payloads, the validation rules and limits.
- **Contracts between repos.** For example: the admin writes HTML that the public app must render; an allow-list that must match in two repos; a field read from one endpoint and written to another.
- **Risks from reading the code.** Edge cases the code handles, and ones it doesn't. Defaults like `value || undefined` that silently drop empty values. Race conditions. Error paths. What unit tests already cover, so manual effort goes elsewhere.
- **What the change does not cover** but the ticket asks for — for example "render rich text on web **and in the apps**" when only web changed.

Label these as risks to check, not bugs. You haven't reproduced anything yet.

## Phase 3: Change → surfaces map

Build this table. It is the heart of the plan and the direct fix for "tested the form, never looked at the result". Keep only the rows that apply.

| Source action | Consumer surface | How to verify | Env / URL |
|---|---|---|---|
| Save a content field | Public page for that record | Rendered DOM + computed styles | staging public URL |
| Add / rename / hide / reorder a nav item | Navigation menu + the route itself | Menu text and order, route loads, hidden = absent | staging home + `/{slug}` |
| Set a record image | Share / preview page | og:image present **and loadable**, width, height, type | public domain |
| Any content field | Public API the apps read | Payload has or lacks the field | API base URL |
| Image with a fallback chain | Same share page, once per fallback step | Remove each level in turn and re-read the tag | public domain |
| Any user-facing text | Other tenants / brands / the production build | Bundle fingerprint; read-only look | other tenant domain |
| Any field another tool can also edit | Legacy admin, CMS, django-admin-style backoffice | Does it show or break the new value format? | ask for the URL if unknown |
| Anything shown in link previews | Crawler-facing raw HTML | Raw HTML fetch. **Chat and tracker link unfurls act as crawlers** — read the preview text of attached links | public domain |
| Anything the native apps render | iOS / Android | Usually blocked. Say so and ask the user or the app team | — |

Publishing steps matter too. A record may need an explicit **publish** or **push changes** action and a visibility flag before it appears anywhere. Test hidden and visible deliberately. A publish action often affects **everyone** on that app, even in a test environment — make it an explicit item in the Phase 5 permission question, and publish only QA records.

## Phase 4: Write the QA ticket

Create it only when the user asked for a ticket. Defaults:

- The dev ticket's team, state `Todo`, assignee `me`, and the dev ticket's cycle/sprint.
- Link it as **related to** the dev ticket and the related backend/frontend tickets. Do **not** make it a sub-issue, so the dev's progress bar isn't touched.
- Labels: read the team's existing labels first. Labels inside a group are often exclusive — one per group.
- Attach the test URLs and MR/PR URLs as links, so they show as attachments.
- Title: `QA: <feature in plain words> (<DEV-ID>)`.
- Use the QA ticket template in `references/templates.md`, written in simple sentences.

After creating it, re-read the issue to confirm links and relations. Also read the **unfurl text of the attached links** — that is what a crawler sees. Add anything odd to the ticket as a "likely bug, please confirm" item.

---

## Phase 5: One permission gate (Run mode)

Ask once, then don't ask again for anything it covered:

- **Where writes may go.** Default and recommended: create dedicated QA records in the **test** environment. Never edit shared or other people's records. **Production is read-only, always** — look, fetch, never save.
- **Shared publishing steps** (publish, push changes, making a QA record visible). These affect everyone on that app, so ask explicitly when the checklist needs them.
- **Where results go.** Default: one comment on the QA ticket, plus ticking the checkboxes that passed.
- Bug tickets and chat messages are **not** covered by this gate. Draft them and ask separately (Phase 8).

If memory or the project notes already record the user's answers, state them back in one line instead of asking again.

## Phase 6: Test data

- **Name it so it is obviously QA:** `[QA] ABC-123 rich text`, or `QA123 OG` when the field is length-limited. Record every ID you create.
- **Keep it invisible where possible.** New records that land hidden by default should stay hidden. Say so in the report.
- **Getting special states.** Use the UI for normal flows. Use the API to create states the UI cannot produce — legacy plain text a new editor can't emit, malformed HTML, oversized values. Duplicate an existing record when you need a realistic starting point, then rename it.
- **Survey real data before inventing it.** List records through the API and group them by shape: empty, plain text, with line breaks, with HTML, with and without related objects. Old data is where regressions hide, and real examples beat made-up ones.
- **Always set the app / tenant / workspace explicitly** in the URL. Pages remember the last selection, which may be a real client's data. Test on a reference or internal tenant, never on a client's.
- **Keep a log of what you change** on your QA records — removed fields, changed dates — so the report can list it.
- **Leave QA records in a useful end state**, for example one record that shows every supported format, so the user can look at it later.

## Phase 7: Execute

Work the checklist in order. For each item:

1. **Act on the source through the real UI**, the way a user would: click, type, save with the page's own buttons. Use the API only to set up states the UI can't create, and say when you did.
2. **Watch the requests.** Install `scripts/browser-helpers.js` and read `window.__qa.reqs`. The request body is the evidence that "saved" really saved the right thing.
3. **Verify on the consumer surface** from the Phase 3 map, in a second tab. Reload twice if the first load shows old data — many apps render a persisted state first.
4. **Record the result immediately:** **pass**, **fail**, **blocked** (reason), **partial** (what was and wasn't covered), or **not run**. Include the literal observed value: message text, status code, computed style, request body. "Works" is not a result.
5. **When something looks wrong, isolate it first:**
   - Repeat with a **control** — an empty value, another record, or the same step on a record without the new feature.
   - Change **one variable at a time** until the trigger is known.
   - Decide whether it is **introduced by this change or pre-existing**: is the responsible code in the diff?
   - **Re-check your own last action.** Did the click land where you meant? Screenshot if unsure.
6. **If a finding affects production or is urgent, tell the user now** — what, where, evidence, who should know — then continue. Don't hold it for the final report.

Break long runs into tracked tasks and mark them as you go. Stop at what is genuinely untestable (native apps, third-party tools behind a login, a crawler user-agent) and mark it blocked with the exact command or step the user can run instead.

### Standard checks

Read `references/standard-checks.md` when writing the checklist and before executing. It lists rendered-content, rich-text/XSS, edge-data, image-upload, save-flow and dirty-state checks.

### When behaviour is unclear

Read the running code before guessing: find endpoints and logic in the loaded JS, copy flows through the API, open failing asset URLs directly to read the server's error body, and capture toasts with `__qa.watch()`. Details: `references/browser-techniques.md`.

### Evidence for every bug: a repro card

A developer must be able to reproduce from the card alone. Use the repro card in `references/templates.md`. When a bug is confirmed, reproduce it once more in a browser that can **save screenshots to disk**, and attach the file to the ticket comment or bug. If no such browser is available, the card must still include the exact URL, test-data ID, numbered steps and the literal request/response. **Never report a bug with only a description.**

## Phase 8: Report

1. **Re-count before posting.** Count pass/fail/blocked per section against the actual checklist items. Totals that don't add up destroy trust in the rest.
2. **Post one results comment** (template in `references/templates.md`), written in simple sentences. Bugs first, sorted by severity, then results per section, then test data and what you changed on QA records. If a posted comment turns out to be wrong, **edit it** instead of adding a second one.
3. **Tick the checkboxes** that passed, one edit per item, anchored on each item's unique leading text (`- [ ] <text>`). Leave fails, blocked and partial items unticked and explain them in the comment. Tick "Done when" lines only if they are fully true.
4. **Bug tickets:** list them as proposals (team, title, severity, one-line why) and ask. Create them only after approval, linked as related to both the QA and dev tickets. A backend bug goes to the backend team even when found through a frontend ticket.
5. **Chat escalation:** only for critical or production-impacting findings. Draft the message (template in `references/templates.md`) and send it only after explicit approval, to the channel or person the user names.
6. **Final chat reply:** verdict first ("source part ready / blocked by X"), then the top findings, what's blocked, and the test data created. Keep it short — the details live in the ticket. If the user wants lasting regression cases from this run, point them at `exploratory-web-testing`.

## Phase 9: Clean up

- **Staged changes:** discard anything staged but not saved. Leave dirty pages with a forced navigation.
- **Viewport:** reset any emulation you set, on every tab you resized.
- **Extra tabs:** close any tab you opened.
- **Interceptors:** reload pages where you forced failures or delays, so nothing stays patched.
- **Test data:** list every record you created, its ID, its visibility, and its final state. Say it in the report.

---

## Files in this skill

Read these when the phase needs them, not all up front:

- `references/environment-map.template.md` — copy to `environment-map.md` and fill in per project: environments, IDs, endpoints, share-link format, known gotchas. Read before Phase 1 on every run.
- `references/adapters/issue-trackers.md` — Linear / Jira / GitHub Issues calls for Phases 1, 4 and 8.
- `references/adapters/code-review.md` — GitLab / GitHub / Bitbucket diff fetching for Phase 1.
- `references/adapters/test-management.md` — optional: pushing results to Qase / TestRail / Zephyr.
- `references/standard-checks.md` — reusable check lists. Read in Phases 3–4 and Phase 7.
- `references/browser-techniques.md` — driving the browser reliably, reading running code, using the helpers. Read before Phase 7.
- `references/templates.md` — QA ticket, results comment, bug repro card, chat escalation draft. Read in Phase 4 and Phase 8.
- `scripts/browser-helpers.js` — paste into the browser console: request log, forced failures, delays, test images, file injection, paste, og-tag check, toast watcher.
