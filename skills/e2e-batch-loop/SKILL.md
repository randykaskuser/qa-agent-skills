---
name: e2e-batch-loop
description: Use when automating end-to-end test cases from an epic, ticket, or test catalogue across multiple pages, screens, or navigation sections — such as "automate ticket QUA-xx", "run the e2e automation loop", "batch automate cases for this section", or when implementing test suites that need to be split into atomic, independently reviewed and merged pull requests. Not for reviewing a single pull request (use code-review) or exploring an app without an automation ticket (use exploratory-web-testing).
---

# E2E Batch Loop

An autonomous, iterative test-automation engine that takes an epic, ticket, or catalogue scope covering multiple application sections, audits live application surfaces against the test catalogue, and delivers 100% P0/P1 automated coverage in strict single-section batches (1 MR per section) with zero-leftover verification, independent code review, and live tracker updates.

**Core principle:** Break large automation scopes into atomic, fully verified single-section batches. Each batch is inspected live, audited against the catalogue, implemented, verified on a live environment, reviewed by an independent subagent, merged via its own MR, and reported to the issue tracker before the next batch begins.

**Violating the letter of the rules is violating the spirit of the rules.**

---

## The Iron Laws

1. **Strict 1 MR Per Unit**: Never combine multiple navigation sections, screens, or feature domains into a single branch or MR. Monolithic PRs create unreviewable diffs, cause CI timeouts, and degrade agent context.
2. **Never Guess Locators**: Always inspect the live target application first, capture full-page screenshots of all states (list, drawers, dialogs, empty states), and ground locators in the live DOM / accessibility tree.
3. **100% P0/P1 Catalogue Completeness**: If the live UI contains critical controls, filters, sorts, or drawers not represented in the catalogue (`docs/test-cases/*.yml`), catalogue them and assign test IDs before writing specs.
4. **Zero Leftovers Invariant**: Every test that writes data must use sandbox naming conventions (e.g. `e2e-` prefix) and clean up after itself. A batch is NOT complete unless the leftover scanner confirms 0 remaining artifacts.
5. **Mandatory Subagent Code Review**: No branch is pushed or merged without an independent fresh-context code review pass (`superpowers:requesting-code-review`). Every finding must be addressed prior to MR creation.

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
10. Update claude-progress.md & Catalogue status
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
- Add new case definitions to the YAML catalogue with sequential IDs (`<PREFIX>-NNNN`).

### Step 3: Isolated Plan & Design Spec
- Create a lightweight plan and design doc under `docs/superpowers/plans/` and `docs/superpowers/specs/`:
  - List of read-only cases vs. write cases.
  - Safety constraints (e.g., display flags set to false, future dates, `e2e-` naming).
  - Target locators and page object methods.

### Step 4: Implementation
- Follow clean Page Object Model / Component structure.
- Encapsulate locators in page objects; keep specs declarative.
- Tag every test with its exact catalogue ID: `test('... @DSH-NNNN', async ({ page }) => { ... })`.
- Separate read-only assertions from write mutations.

### Step 5: Two-Stage Verification
- **Stage 1 (Offline Baseline):** Run `./init.sh` or `make check` (must pass typecheck, unit tests, and catalogue enumeration).
- **Stage 2 (Online Execution):** Run the spec against the live target environment (e.g. `testing` or `staging`). All tests must pass, or skip with an authorized categorized reason.

### Step 6: Zero-Leftover Verification
- Run the repository leftover check (e.g. `npm run leftovers -- <target>`).
- If any `e2e-` test entities remain, diagnose the cleanup failure, fix the fixture/teardown, delete the leftover, and re-verify.

### Step 7: Subagent Code Review
- Dispatch a fresh reviewer agent using `superpowers:requesting-code-review`.
- Review against: locator fragility, test isolation, race conditions, cleanup reliability, and style consistency.
- Apply all fixes before proceeding.

### Step 8: VCS Branch, Commit & Merge Request
- Create a feature branch: `test/<ticket-id>-<section-name>`.
- Commit with standard attribution:
  ```
  test(<section>): automate <N> <Suite> -> <Section> cases (<TICKET-ID>)
  
  Co-Authored-By: Claude Code <noreply@anthropic.com>
  ```
- Push branch and create a Merge Request / Pull Request.
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
- Update `claude-progress.md` with the completed section and the next target.
- Update catalogue YAML: set `automation: automated` for all completed cases.
- If more sections remain in the ticket, immediately loop to Step 1 for the next section.
- If all sections in the ticket are complete:
  - Run full suite baseline.
  - Transition ticket status to `Done`.
  - Post final summary comment to Linear.

---

## Rationalization Table

| Excuse / Rationalization | Reality & Hard Rule |
|---|---|
| *"These two sections are small; let's combine them into one MR."* | **Forbidden.** Combining sections dilutes review focus, complicates rollbacks, and risks failing CI pipelines. Keep it strictly 1 MR per section. |
| *"I already know how this form works; I don't need to take screenshots."* | **Forbidden.** Visual inspection catches unexpected tabs, altered labels, and broken responsive states. Always inspect live. |
| *"I'll clean up the test entities manually later."* | **Forbidden.** Automated teardown must be proven live. Leftovers scanner must show 0 immediately. |
| *"Code review is slow; I'll self-review this time."* | **Forbidden.** A fresh subagent catches blind spots (unhandled promises, locator race conditions, missing tags). |
| *"The catalogue doesn't have an ID for this filter, so I won't test it."* | **Forbidden.** Your job is 100% P0/P1 coverage. Add the missing case to the catalogue first, then automate it. |
| *"The test passed locally, so I don't need to run live on staging."* | **Forbidden.** Staging environments exhibit CORS, latency, permissions, and hydration quirks not present in mocks. |

---

## Red Flags List

If you catch yourself thinking any of these, STOP immediately and return to the lifecycle:
- "I'll create one branch for the whole ticket."
- "The leftover count is only 1, probably from an earlier run."
- "I'll open the PR first and run the tests while CI builds."
- "I don't need to update `claude-progress.md` until the whole ticket is done."
- "Let's skip the code review subagent because the changes look straightforward."

---

## Adapter Configuration by Repository

| Configuration | `e2e-dashboard` | `e2e-website` | `e2e-mobile` |
|---|---|---|---|
| **Catalogue File** | `docs/test-cases/dashboard.yml` | `docs/test-cases/web-player.yml` | `docs/test-cases/mobile-app.yml` |
| **Case ID Prefix** | `DSH-NNNN` | `WEB-NNNN` | `MOB-NNNN` |
| **Batch Unit** | Sidebar navigation section | Screen or Player domain | App tab or feature flow |
| **Baseline Command** | `./init.sh` or `make check` | `./init.sh` or `npm test` | `./init.sh` or `npm run check` |
| **Live Test Command** | `ALLOW_WRITES=<target> npx playwright test <spec> --project=<target>` | `npm run test:<target> <spec>` | `npm run test:device <spec>` |
| **Cleanup Command** | `npm run leftovers -- <target>` | Teardown API / fixture checks | App sandbox state reset |
| **Safety Invariants** | `e2e-` prefix, display flags false, date limits | Cloudflare bypass token, guest writes | Dedicated test org, isolated user accounts |
