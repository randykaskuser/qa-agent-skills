# Adapter — issue trackers

The workflow in `SKILL.md` needs six things from a tracker. This file maps them onto the
common ones. Use whichever adapter matches the project; the phases don't change.

| # | What the workflow needs | Phase |
|---|---|---|
| 1 | Read a ticket **with its relations** | 1 |
| 2 | Keyword-search for related work that isn't linked | 1 |
| 3 | Read the team's label set | 4 |
| 4 | Create a ticket, related-to (not sub-issue), with attached links | 4 |
| 5 | Comment, and edit that comment later | 8 |
| 6 | Tick checkboxes in the ticket body | 8 |
| 7 | Attach a screenshot file | 7–8 |

---

## Linear

Via the Linear MCP connector.

| Need | Call |
|---|---|
| 1 | `get_issue` with `includeRelations` |
| 2 | `list_issues` with `query: "<distinctive term>"` |
| 3 | `list_issue_labels` for the team |
| 4 | `save_issue` — set `team`, `state: Todo`, `assignee: me`, the dev ticket's `cycle`, `relatedTo: [<dev ticket>, …]`, and `links` for test and MR URLs |
| 5 | `save_comment`; to edit, `save_comment` again with the existing `id` |
| 6 | `save_issue` with `patch` ops — one `replace` per passed item, anchored on `- [ ] <unique leading text>` |
| 7 | `prepare_attachment_upload`, then `create_attachment_from_upload` |

Notes:

- **Related, not sub-issue.** A sub-issue changes the dev ticket's progress bar.
- Labels inside a group (for example a *Products* group) are **exclusive** — one per group.
- After creating, re-read the issue and read the **unfurl text of attached links**. That is what
  a crawler sees, and it has caught real og-tag bugs.

## Jira

Via a Jira MCP connector or the REST API.

| Need | Call |
|---|---|
| 1 | `jira_get_issue`, then `jira_get_issue_links` for relations |
| 2 | `jira_search_issues` with JQL: `project = ABC AND text ~ "og:image" ORDER BY updated DESC` |
| 3 | `jira_get_all_labels`, or `jira_get_create_metadata` for the fields a project actually allows |
| 4 | `jira_create_issue`, then `jira_create_issue_link` with type `Relates` |
| 5 | `jira_add_comment`; edit through the comment update endpoint |
| 6 | `jira_update_issue` on the `description` field — read it, replace the `[ ]` markers, write it back |
| 7 | `jira_upload_attachment` |

Notes:

- Jira has no native checkbox list. Use a markdown/wiki checklist in the description and edit the
  text, or a checklist app if the project has one — say which you used.
- `Relates` is the safe link type. `Blocks` and `is caused by` change other people's boards.
- Sprint = cycle. Read it from the dev ticket and reuse it.

## GitHub Issues

Via the `gh` CLI or the REST API.

| Need | Call |
|---|---|
| 1 | `gh issue view <n> --json title,body,labels,milestone,comments` |
| 2 | `gh issue list --search "og:image" --state all` |
| 3 | `gh label list` |
| 4 | `gh issue create --title … --body-file … --label … --milestone …` |
| 5 | `gh issue comment <n> --body-file …`; edit with `gh issue comment --edit-last` or the API |
| 6 | `gh issue edit <n> --body-file <updated body>` — GitHub renders `- [x]` natively |
| 7 | No attachment API. Commit the screenshot to a branch or a gist and link it, and say so |

Notes:

- GitHub has no typed "relates to". Cross-reference by mentioning `#<dev issue>` in the body;
  that creates a visible backlink both ways.
- Sub-issues exist on newer GitHub plans. Prefer a plain cross-reference so the dev's tracking
  is untouched.

---

## No tracker connected

Still do every phase. Write the QA ticket and the results comment as markdown files, deliver them
to the user, and say clearly in the final reply that nothing was posted anywhere.
