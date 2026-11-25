---
name: write-playwright-tests
description: Turn requirements (PRD, Jira ticket, user story) into working Playwright tests by inspecting the live app through the Playwright MCP, then run and fix them. Use when the user wants Playwright tests written for one flow or feature. Not for architecture decisions or code review (use automation-architecture), or for automating a whole ticket section by section with one MR each (use automate-ticket-in-batches).
---

# Playwright Robot

Turn raw requirements (PRD, Jira, user stories) into maintainable Playwright suites, grounded in the live app.

## 1. Requirement Analysis
Before writing any code, analyze the input requirements.
- Identify the core user journey.
- Assess risks and edge cases.
- Outline the test scenarios to be covered.
- Clearly state the scope of what will be automated (and what will be omitted, e.g., third-party auth).
- Ask the user for the target URL if not provided.

## 2. Live Inspection (Playwright MCP)
**Do not guess selectors.** You must scout the live application using the Playwright MCP to find resilient locators.
- Use `browser_navigate` to open the target URL.
- Use `browser_snapshot` to capture the accessibility tree and find robust locators (prefer `getByRole`, `getByText`, `getByLabel`).
- If interacting with a flow (like a checkout), use `browser_click`, `browser_fill_form`, etc., to move through the flow and snapshot each state.
- Note any specific network requests to wait for if the page is dynamic.

## 3. Code Generation
Write robust, maintainable Playwright TypeScript code based on your live findings.
- **Monorepo Awareness:** Check the current workspace structure. If there is an existing `web/` directory containing a `playwright.config.ts`, put all tests and page objects inside that `web/` directory (e.g., `web/tests/`, `web/pages/`).
- **Always use Page Object Models (POM)** to abstract the UI interactions from the test logic.
- Ensure the code follows Playwright best practices (e.g., using `await expect()`, relying on auto-waiting).
- Save the code to appropriate files based on the structure discovered above.

## 4. Run, Validate & Self-Fix
Finish with a run whose result you can explain: the tests pass, or a failure is a product bug you report.
- Use the terminal (Bash/PowerShell) to execute the test.
- **Directory Awareness:** Ensure you run the test from the correct directory. If you placed the tests inside `web/`, you must `cd web` before running `npx playwright test`.
- Read the output logs.
- If the test fails:
  1. Analyze the failure reason.
  2. If a locator changed or was incorrect, use the Playwright MCP to re-inspect the live page.
  3. Apply the fix and re-run the test.
- Fix test faults (locator, wait, data) and re-run. If the app itself is wrong, keep the assertion, report the bug with evidence, and stop; weakening the assertion would hide it.

## Getting Started
When invoked, begin immediately with Step 1 and present your Requirement Analysis to the user before proceeding to Step 2.
