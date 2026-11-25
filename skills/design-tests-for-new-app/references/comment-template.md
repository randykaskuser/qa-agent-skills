# Ticket comment

One comment per ticket, owned by QA, edited on every rerun. The first line is fixed so a rerun can find it.

## House format first

If the project's earlier comments already follow a format (e.g. a case table with Priority and Change columns plus Steps / Proof lines), keep it. On a rerun, edit in that format; do not convert it to the template below. Check only that it carries what the template carries: every case with its priority and a link, the ticket lines not tested and why, and how to post proof. Use the template only when no format exists yet.

## Template

```markdown
**Test cases (QA, updated 19 Nov 2026)**

**Cases:** [WEB-0125](<case url>) Mini player stays visible while scrolling (P1) · [WEB-0141](<case url>) … (P2)
**Covers:** AC1 → WEB-0125 · AC2 → held, see QUA-200
**Not tested:** AC3 uses the new component (code only) · AC4 analytics event
**Needs AC:** dark mode has a design link only
**How to verify:** run the P0/P1 cases on <build / environment>, post proof (screenshot or video per case) here.
```

- Drop a line that has nothing in it. Never more than these six lines plus the header.
- Case links use the QA Tools case URL from the settings block, when there is one.
- Held lines name the conflict ticket; they never describe the ruling you expect.

## Rerun: edit, don't add

1. List the ticket's comments. Find the ones whose body starts with `**Test cases (QA, updated` (or `Test cases (QA, updated` without bold).
2. **One found** → update it with its comment id (Linear `save_comment` with `id`). New date in the header.
3. **None** → create it.
4. **Two or more** → update the oldest; list the others in the report and ask before deleting (a delete cannot be undone).
5. Body unchanged apart from the date → do not touch it.
