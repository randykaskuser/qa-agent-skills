---
name: automate-ticket-in-batches
description: Use when automating end-to-end test cases from an epic, ticket, or test catalogue across multiple pages, screens, or navigation sections — such as "automate ticket QUA-xx", "run the e2e automation loop", "batch automate cases for this section", or when implementing test suites that need to be split into atomic, independently reviewed and merged pull requests. Not for reviewing a single pull request (use code-review) or exploring an app without an automation ticket (use explore-app-without-spec).
---

# E2E Batch Loop

An autonomous, iterative test-automation engine that takes an epic, ticket, or catalogue scope covering multiple application sections, audits live application surfaces against the test catalogue, and delivers 100% P0/P1 automated coverage in strict single-section batches (1 MR per section) with zero-leftover verification, independent code review, and live tracker updates.

**Core principle:** Break large automation scopes into atomic, fully verified single-section batches. Each batch is inspected live, audited against the catalogue, implemented, verified on a live environment, reviewed by an independent subagent, merged via its own MR, and reported to the issue tracker before the next batch begins.

---

## Rules

1. **Strict 1 MR Per Unit**: Never combine multiple navigation sections, screens, or feature domains into a single branch or MR. This holds for small sections too: combined diffs are hard to review and roll back, and can time out CI.
2. **Never Guess Locators**: Always inspect the live target application first, capture full-page screenshots of all states (list, drawers, dialogs, empty states), and ground locators in the live DOM / accessibility tree. A familiar form still gets inspected, because live pages show changed labels, extra tabs and broken states the code does not.
3. **100% P0/P1 Catalogue Completeness**: If the live UI contains critical controls, filters, sorts, or drawers not represented in the catalogue (`docs/test-cases/*.yml`), catalogue them and assign test IDs before writing specs.
4. **Zero Leftovers Invariant**: Every test that writes data must use sandbox naming conventions (e.g. `e2e-` prefix) and clean up after itself. A batch is complete only when the leftover scanner reports 0, and an artifact from an earlier run counts: clean it up rather than explaining it away.
5. **Mandatory Subagent Code Review**: Run an independent fresh-context review (`superpowers:requesting-code-review`) and address every finding before pushing, including for straightforward changes: a fresh reader catches unhandled promises, locator races and missing tags.

---

## Batch Lifecycle (Step-by-Step per Section)

```
[Start Section Batch]
         │
         ▼
 1. Live Inspection & Screenshots (docs/screenshots/<section>/)
         │
         ▼
 2. Catalogue Gap Audit (docs/test-cases/*.yml -> 100% P0/P1)
         │
         ▼
 3. Section Plan & Design Spec (docs/superpowers/{plans,specs}/)
         │
         ▼
 4. Implement POMs & Specs (@<PREFIX>-NNNN)
         │
         ▼
 5. Two-Stage Verification
    ├─ Offline: ./init.sh / typecheck / unit tests
    └─ Online: live test execution on target environment
         │
         ▼
 6. Zero-Leftover Assertion (leftovers == 0)
         │
         ▼
 7. Subagent Code Review (superpowers:requesting-code-review)
         │
         ▼
 8. Git Commit, Branch & MR (1 MR per section, arm auto-merge)
         │
         ▼
 9. Post Scannable Linear Comment
         │
         ▼
10. Update progress record & Catalogue status
         │
         ▼
[Next Section in Ticket Scope]
```

### Step 1: Live Surface Inspection & Evidence
- Navigate to the live page/screen using browser tools.
- Capture full-page screenshots of:
  - List / Overview view (with data and empty state if possible).
  - Create / Add drawer or modal.
  - Edit drawer / modal (populated with existing entity).
  - Specialized dialogs (bulk actions, filters, deletion confirmations).
- Save screenshots into `docs/screenshots/<section>/`.

### Step 2: Catalogue Audit & Gap Analysis
- Read the project's test catalogue (`docs/test-cases/<domain>.yml`).
- Compare live controls, tabs, and validations against the catalogue.
- Discover any uncatalogued P0/P1 features (e.g. column sorting, reset filters, duplicate actions, pagination, tab persistence).
- An editable field the catalogue covers only with a "set" case also needs clear and replace cases: save, reload, and the request sends null or empty, not the old value.
- Add new case definitions to the YAML catalogue with sequential IDs (`<PREFIX>-NNNN`).

### Step 3: Isolated Plan & Design Spec
- Create a lightweight plan and design doc under `docs/superpowers/plans/` and `docs/superpowers/specs/`:
  - List of read-only cases vs. write cases.
  - Safety constraints (e.g., display flags set to false, future dates, `e2e-` naming).
  - Target locators and page object methods.

### Step 4: Implementation
- Follow clean Page Object Model / Component structure.
- Encapsulate locators in page objects; keep specs declarative.
- Tag every test with its exact catalogue ID: `test('... @<PREFIX>-NNNN', async ({ page }) => { ... })`.
- Separate read-only assertions from write mutations.

### Step 5: Two-Stage Verification
- **Stage 1 (Offline Baseline):** Run `./init.sh` or `make check` (must pass typecheck, unit tests, and catalogue enumeration).
- **Stage 2 (Online Execution):** Run the spec against the live target environment (e.g. `testing` or `staging`). All tests must pass, or skip with an authorized categorized reason. Run live even when local passes: CORS, latency, permissions and hydration differ.

### Step 6: Zero-Leftover Verification
- Run the repository leftover check (e.g. `npm run leftovers -- <target>`).
- If any `e2e-` test entities remain, diagnose the cleanup failure, fix the fixture/teardown, delete the leftover, and re-verify.

### Step 7: Subagent Code Review
- Dispatch a fresh reviewer agent using `superpowers:requesting-code-review`.
- Review against: locator fragility, test isolation, race conditions, cleanup reliability, and style consistency.
- Apply all fixes before proceeding.

### Step 8: VCS Branch, Commit & Merge Request
- Create a feature branch: `test/<ticket-id>-<section-name>`.
- Commit as `test(<section>): automate <N> <Suite> -> <Section> cases (<TICKET-ID>)`, with the attribution lines your environment or the repo specifies.
- Push the branch and create the Merge Request / Pull Request only after Steps 5-7 pass; do not open it while the tests still have to run.
- Arm auto-merge on pipeline pass, or squash-merge if authorized.

### Step 9: Scannable Linear Comment
Post a progress comment to the Linear ticket following the team's strict formatting:
- **Bold status header**: `### <Suite> -> <Section> Automated (<N> cases, MR !XX)`
- **Bullet points with bold labels**:
  - **Coverage**: Total cases (read-only vs write), list of IDs.
  - **Features covered**: Specific controls and user journeys automated.
  - **Verification**: Baseline check status, live pass rate, 0 leftovers confirmed.
  - **MR**: Direct link to the MR.
  - **Next**: Name of the next section in the ticket scope.
- **No conversational filler** (no "I'm pleased to report", "Hope this helps").

### Step 10: Progress Tracking & Loop Continuation
- Record the completed section and the next target after every section, not once at the end of the ticket, in the place the `progress` setting names. Without that setting, follow the repo's AGENTS.md or CLAUDE.md; create no new progress file.
- Update catalogue YAML: set `automation: automated` for all completed cases.
- If more sections remain in the ticket, immediately loop to Step 1 for the next section.
- If all sections in the ticket are complete:
  - Run full suite baseline.
  - Transition ticket status to `Done`.
  - Post final summary comment to Linear.

---

## Repository settings

Read the `## E2E batch settings` block in the repo's CLAUDE.md. If it is missing, ask once for the values and propose the block.

```markdown
## E2E batch settings
- catalogue: docs/test-cases/<domain>.yml
- id_prefix: <PREFIX>-NNNN
- batch_unit: <sidebar section | screen | app tab>
- baseline: <command>
- live_test: <command>
- cleanup: <command>
- safety: <naming prefix, flags, date limits, test org>
- progress: <file and field that record the session state>
```
