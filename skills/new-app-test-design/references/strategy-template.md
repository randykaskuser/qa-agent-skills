# Settings, comparison, strategy and plan

## Settings block

The repo's CLAUDE.md holds one block. The skill reads it; it never hard-codes these.

```markdown
## Test design settings
- catalogue: docs/test-cases/mobile-app.yml
- id_prefix: MOB-
- qa_tools_product: mobile
- linear_teams: IOS, AND
- qa_team: QUA                                 # optional: where scoping / plan / conflict / automation tickets go
- case_url: https://<qa tools>/?product=mobile#/cases?case={id}   # optional
```

Web example: `docs/test-cases/web-player.yml`, `WEB-`, `web`, `WEB`.
Block missing → ask for the four required values once, propose adding the block, and use the answer for this run.

## Comparison doc — `docs/<project>/<project>-vs-current.md` (phase 2)

Lead line: what the new app is and which apps run it.

1. **Platform and build** — how the new app is built and installed; environment; app ids.
2. **One section per area** (shell and navigation, theme and layout, content types, flows outside content, account) — table: today · new · test impact.
3. **Not in the new app yet** — so no case is written for it.
4. **What it means for the cases** — counts per bucket (classic only / new only / both same / both different) and the open questions for the gate.
5. **Design links** — the design file and frames used.

Publish an artifact view of it (load `artifact-design` first) and link both from the scoping ticket.

## Strategy doc — `docs/<project>/test-strategy.md` (phase 3, MR)

Lead line: where cases live, how they are tagged, who runs them.

1. **Goals** — from the kick-off call or ticket, numbered.
2. **Where cases live** — options table (same catalogue + app tags / new catalogue / new field) with a verdict; tag rules (the four buckets); guard (which check fails on an untagged case).
3. **How cases are structured** — fields, priority → scope table, ticket links.
4. **Which existing cases apply** — link to the sweep or the comparison doc §4.
5. **How cases are run** — phases (manual by developers, QA build, automation, release regression).
6. **Order of work** — numbered.
7. **Open decisions** — one line each, with who decides.

## Test plan (Confluence, phase 3; via `confluence-writer`)

Scope (in / out), environments and builds, entry and exit criteria (release rule: every P0 passes), case counts per priority and bucket, schedule, risks, conflicts link, coverage artifact link. Each later change = a new version with a one-line change note; never a second page.

## Tickets in the QA team

| Ticket | Phase | Body |
|---|---|---|
| Scoping | 2 | comparison links, bucket counts, tag names to approve |
| Plan | 3 | strategy MR, Confluence link, sign-off checklist |
| Cases | 4–6 | case range, reviewer findings applied, coverage artifact link |
| Conflicts | 5 | see conflict-ticket.md (Blocked) |
| Automation | 7 | automatable count by area, `blocked_by` list, what must exist first |

Find each by title before creating it; reuse on rerun.
