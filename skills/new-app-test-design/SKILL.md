---
name: new-app-test-design
description: Use when a new app version, a rebuilt app or a big feature set needs QA test design from its tickets, mobile or web — "scope X for QA", "do the same as <last project> for web", "write cases for milestone Y", a Linear project or milestone link — and when picking up or repairing such a pass that was started earlier, by hand or by another session.
---

# New app test design

Tickets in, five checkable outputs out: a today-vs-new comparison, a strategy and test plan, catalogue cases, one comment per ticket, and cases marked ready for automation. Each phase ends in an output someone can check; each gate stops for the owner.

**Core rule:** every expected line traces to a ticket line. What no ticket says gets no case; what two tickets say differently gets no case until the product owner rules.

## Start here, every time

1. **Settings.** Read the `## Test design settings` block in the repo's CLAUDE.md. Format and fallback: [references/strategy-template.md](references/strategy-template.md#settings-block). Missing → ask once for the four values and propose the block.
2. **Inventory (resume / repair mode).** Before any write, look for earlier work on this project: comparison and strategy docs, sweep doc, catalogue cases carrying the project tag (id range), Linear comments starting `Test cases (QA, updated`, the coverage artifact URL, the Confluence plan and its version, a conflict ticket, scoping / plan / automation tickets. Run `scripts/apply_patches.py <catalogue> --prefix <P> --check --ids <range>`.
3. **Report a table** — output, exists (link), missing, breaks a rule — then continue from the first phase with a gap. Fix only what is missing or broken. Existing outputs are edited in place: same comment, same artifact URL, next plan version, same conflict ticket.

## Phases

| # | Phase | Output (checkable) | Gate |
|---|---|---|---|
| 1 | **Intake** | ticket list: id, team, status, ACs, comments, design links. No writes. | — |
| 2 | **Scope** | comparison doc + artifact (today vs new); every existing case in one of four buckets; QA scoping ticket | **tag names and bucket split** |
| 3 | **Strategy + plan** | `docs/<project>/test-strategy.md` (MR); Confluence test plan (`confluence-writer`); QA plan ticket | **sign-off** |
| 4 | **Cases** | new catalogue cases from ACs and observed behaviour, written as patch JSON, applied with `apply_patches.py` | — |
| 5 | **Gap + conflict passes** | patch JSON from two fresh reviewers; one Blocked conflict ticket | **who rules the conflicts** |
| 6 | **Publish** | one comment per ticket; coverage artifact; plan version bump | — |
| 7 | **Automation handoff** | every regression case `automatable` or `not-automatable` + `reason` / `blocked_by`; QA automation ticket | stop |

**Four buckets** (phase 2): classic only (old tag) · new only (new tag) · both, same steps (one case, both tags) · both, different steps (two cases: old untouched, new beside it). A case holds one set of steps.

**Fresh reviewers** (phase 5): two subagents, one for AC coverage, one for edge cases. Give each the ticket text, the cases for it and [references/case-rules.md](references/case-rules.md); never your reasoning. Each returns patch JSON (`edits` / `new`). Apply all patches in one `apply_patches.py` run; it keeps unchanged cases byte for byte and numbers new ones.

**Conflicts:** two tickets that disagree → one entry in the single conflict ticket ([references/conflict-ticket.md](references/conflict-ticket.md)), no case, no "on hold" case, not a ticket comment. Cases come after the ruling.

**Publish:** comments per [references/comment-template.md](references/comment-template.md) (keep an existing house format). Coverage page: `scripts/build_coverage.py --help` (rows: one per feature, any number of ticket teams), then the Artifact tool — republish to the stored URL.

**Stop at phase 7.** Mark cases and open the ticket. Never write Maestro, Playwright or other flows here.

## Hand-offs

- `confluence-writer` — the test plan page and each version bump.
- The project's knowledge skill (e.g. `audiospace-qa:audiospace-knowledge`) — real field, route and endpoint names for steps.
- `artifact-design` — before the comparison or coverage page.

## Common mistakes

| Mistake | Instead |
|---|---|
| Case for "fire the analytics event" or "use component X" | No case. List it under "not tested" in the ticket comment. |
| "On hold" case for two conflicting tickets | No case; conflict ticket entry. |
| 3 steps, 1 expected paragraph | Pairs 1:1; `apply_patches.py` fails otherwise. |
| Feature AC rated P2 | AC = P1; P0 only when the core flow breaks for everyone; edge = P2/P3. |
| New comment on rerun; new artifact URL; new Confluence page | Edit the `Test cases (QA, updated …)` comment; same URL; next version. |
| Reformatting every existing comment to the template | Keep the project's format; edit only what changed. |
| P0 on every case of a feature | P0 = core flow broken for everyone; check the P0 share in the inventory (RESC: 50 → 18 after review). |
| Inventing tags or the split without asking | Phase 2 gate. |
| Writing automation specs "while we're here" | Phase 7 stops at marking. |
| Redoing a pass someone started | Inventory first; fix only gaps and rule breaks. |
