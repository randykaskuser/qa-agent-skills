# Conflict ticket

All contradictions between tickets of one project go into **one** ticket in the QA team, status **Blocked**, assigned to the person who rules (asked at the phase 5 gate). No case is written for a conflict until it is ruled.

## Find before you create

Search the QA team for an open ticket titled `[<project>] Conflicts to rule` (or one linked from the strategy doc). Found → add entries to it. Not found → create it.

## Template

```markdown
**<N> conflicts between <project> tickets need a ruling. No test case is written for them until then.**

### 1. <short name, e.g. Mini player close>
- **Tickets:** WEB-502 AC2, WEB-504 AC1
- **WEB-502 says:** "Closing the mini player stops playback."
- **WEB-504 says:** "Closing the mini player pauses playback; reopening resumes at the same position."
- **Question:** stop or pause-and-resume?
- **Held:** cases for WEB-502 AC2 and WEB-504 AC1.

### 2. …

**Next:** reply per number; QA writes the cases and updates the ticket comments.
```

- Quote each ticket line exactly (short); never paraphrase it into agreement.
- One numbered entry per conflict. On rerun, add new entries at the end; never renumber.
- When an entry is ruled: write the cases, update the ticket comments, mark the entry `Ruled <date>: <answer> → <case ids>`. Close the ticket when every entry is ruled.
- Link the ticket from the strategy doc and the coverage artifact banner.
