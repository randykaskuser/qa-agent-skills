---
name: verify-bug-fix
description: Use when a reported bug is marked fixed, resolved or ready for QA and must be retested before the ticket is closed — "is ABC-12 really fixed?", "dev says it's fixed, verify it", "retest last week's bugs on staging", one ticket or a batch — including when the fix only partly holds and the ticket goes back to the developer. Not for testing a new feature or change against its acceptance criteria (use test-a-ticket).
license: "MIT"
---

# Verify Bug Fix

Retest a reported bug on the build that claims the fix, give one verdict per ticket, and hand back proof: a before/after image when it passed, a repro card when it did not.

**Core rule:** a fix passes only when every check passes on the stated build. A check fails the fix when it sits inside the original bug's steps or the ticket's acceptance criteria. A failure outside both is a new bug: propose it separately, and the fix can still pass.

## Steps

1. **Gather, per ticket:** the original steps, expected and actual, the bug-report proof image (ticket description, comments, an earlier results page), the acceptance criteria, and the build or merge request that claims the fix. Confirm that build is the one deployed where you test; a merged MR is not a deploy.
2. **Write the checks before testing.** Check 1 is the original repro, step for step. Add two to four nearby cases the fix could miss: the same action after an edit, after a reload, from another entry point, and each other clause of the acceptance criteria.
3. **Retest through the real UI.** Watch the request and response for every save. Screenshot each result and crop the same region as the Before proof; leave out sidebars and personal data. A check with no screenshot stays text only and names its evidence, such as the response value.
4. **Verdict per ticket:** *passed* (every check passed), *not fixed* (a check failed, per the core rule) or *blocked* (the state could not be reached; say why).
5. **Hand back:**
   - **Passed:** **REQUIRED SUB-SKILL:** use qa-agent-skills:report-test-results (run type: fix retest, with `--png`). Review each PNG as that skill says, then post it with its one-line comment: "QA passed on <env> <build>: <what now works>."
   - **Not fixed:** no before/after image. The comment is the repro card: "Not fixed on <env> <build>: <failing check>.", then steps, expected, actual, build and date. Attach the cropped screenshot with the failing part boxed in red (`compare_panels.py` in report-test-results, `RED`). Propose moving the ticket back to the developer; change its status only after the user agrees.
   - **Blocked:** comment what blocks the retest and what would unblock it. No verdict.
6. **Reply with one row per ticket:** id, verdict, the failing check if any, comment link. Verdicts first; a deadline or a "main case works" does not change one.

## Quick reference

| Situation | Verdict | Output |
|---|---|---|
| Original repro and nearby checks pass | passed | before/after PNG + one-line comment |
| Original repro passes, an AC clause fails | not fixed | repro card, propose reopening |
| Something unrelated broke | passed + new bug | PNG, and a proposed new ticket |
| Fixed build not deployed, or no test data | blocked | what blocks it |

## Common mistakes

| Mistake | Fix |
|---|---|
| Only the original steps retested | Add the nearby checks in step 2 |
| Full-page screenshots | Crop the region of the Before proof |
| New Before screenshot taken on the fixed build | Before is the bug-report proof, or text only |
| Status changed without asking | Propose; the user decides |
