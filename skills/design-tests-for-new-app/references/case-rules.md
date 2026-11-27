# Case rules

Every author and every reviewer works from this page. `scripts/apply_patches.py --check` enforces the mechanical ones; the rest are judgment.

## What gets a case

1. **Every expected line traces to a ticket line**: an AC, a ticket comment from the developer or designer, a design frame, or behaviour you observed on a build. Name the source in `description` ("Sources IOS-12 AC2, AND-34 comment").
2. **No case for code-level ACs** ("use component X", "migrate to the new client", "refactor"). Nothing a tester sees changes. List them under "Not tested" in the ticket comment.
3. **No case for analytics or tracking ACs** ("fire `article_view`"). Same: "Not tested" in the comment.
4. **No case for a ticket with no AC and only a design link** until the design is read into concrete expected lines, or the ticket is listed as "needs AC" in the comment.
5. **Conflicting requirements get no case.** Two tickets (or a ticket and a design) that say different things go to the conflict ticket. No "on hold" case, no case that picks one side.
6. **Clear and replace.** A field the user can set (image, optional field, date, choice) gets a set case, a clear case and a replace case. Their expected lines include "after a reload" and, where the tester can see it, the saved value (empty, not the old one).
7. **Same field, other screens.** When a ticket's field is also written by other screens or APIs (admin vs user view, web vs mobile, bulk vs single, old vs new editor), each writer gets its own set, clear and replace cases, tagged for the screen. List the writers in phase 1. A writer you cannot confirm goes on the open questions in the ticket comment, not silently left out.
8. **Side fixes in comments.** A developer comment such as "also fixed X" or "found along the way" makes X a case, sourced to that comment ("Sources WEB-506 comment"). It is P1 when X was broken, since no other ticket covers it.
9. **One case per tester pass**: one setup, one walk through the app, one account state. A second account, a second build, or a reinstall is a second case.

## Shape

- **Steps and expected are paired 1:1**: step 3's result is expected line 3. Same count, always.
- One action per step. Expected lines say what the tester sees, not what the code does.
- `preconditions` names the build, environment, app/screen ids and account type (guest or which test account, never its credentials).
- Never copy credentials, tokens or API keys from a ticket into a case.

## Priority, scope, type tag

| Priority | Means | Scope | Type tag | Automation |
|---|---|---|---|---|
| **P0** | release blocker: a core flow broken for everyone | regression | `smoke` or `regression` | `automatable` / `not-automatable` |
| **P1** | a feature AC | regression | `regression` | `automatable` / `not-automatable` |
| **P2** | edge case, likely | extended | `extended` | `manual` |
| **P3** | edge case, rare | extended | `extended` | `manual` |

- The type tag must match the scope. A scope that differs from the priority needs a `reason`.
- Release rule to state in the plan: every P0 must pass; a failing P1 gets a bug ticket but does not block.

## App tags (four buckets)

Set in phase 2 and approved at its gate. Example names: `classic` (today's app) and `v2` (the new one).

| Case applies to | Tags | Action |
|---|---|---|
| today's app only | old | leave as is |
| new app only | new | new case |
| both, same steps | old + new | one case, add the new tag (after it passes once on a new build, if the strategy says so) |
| both, different steps | old on the old case, new on a new case | old case untouched, new case beside it |

## Automation fields (phase 7)

- `automatable`: a flow could check every expected line on a test build.
- `not-automatable` + `reason`: a visual judgment, a physical device action, a third-party sign-in, etc.
- `blocked_by`: what must exist first (a QA build, stable ids, test content). Free text, short.
- P2/P3 stay `manual`.

## Patch JSON (authors and reviewers return this)

```json
{"edits": [{"id": "WEB-0133", "set": {"expected": "1. ...\n2. ...\n3. ...\n4. ..."}}],
 "new": [{"sibling": "WEB-0125", "row": 4, "covers": "WEB-506 AC2",
          "title": "Queue keeps the new order after a reload", "priority": "P1",
          "description": "... Sources WEB-506 AC2.", "preconditions": "...",
          "steps": "1. ...\n2. ...", "expected": "1. ...\n2. ...", "tags": ["web", "v2", "regression"]}]}
```

- `sibling`: an existing case to copy the other fields from (suite, tiers, flags).
- `row`: the coverage row it belongs to; `covers`: the ticket lines it proves.
- Scope, type tag and automation are fixed from the priority by the script.

## Reviewer brief (phase 5)

Send each reviewer: this page, the ticket text (ACs, comments, design notes), the cases that cite it. Not the author's reasoning.

- **AC reviewer:** for every AC line, which case proves it? Missing → `new`. Expected line with no source → `edits` or flag. Code/analytics AC with a case → flag.
- **Edge reviewer:** empty, long, offline, slow, denied permission, second device, expired session, rotation, theme, locale. Only where the ticket's feature can hit it; P2/P3.
- Both: report contradictions between tickets as a list, not as cases.
