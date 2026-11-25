# Adapter — code review platforms

Phase 1 needs three things from the forge:

1. The **description** of the merge/pull request.
2. The **diffs**, skipping lockfiles.
3. The **target branch** — a change merged to a shared integration branch is not "live everywhere".

## If the agent sandbox cannot reach the forge

This is the normal case for self-hosted forges and for hosts behind a bot check. Don't fight it:

1. Open a page on the forge host in the user's logged-in browser.
2. If a bot check appears, one reload usually clears it. **If it persists, ask the user to click it.
   Never solve a CAPTCHA yourself.**
3. Call the forge's REST API **from the page context**, so the session cookie is used.

That gives you authenticated API access without handling any credential.

---

## GitLab

```js
const p = encodeURIComponent('group/subgroup/project');
const mr   = await fetch(`/api/v4/projects/${p}/merge_requests/205`).then(r => r.json());
const diff = await fetch(`/api/v4/projects/${p}/merge_requests/205/diffs?per_page=100`).then(r => r.json());
mr.target_branch;                       // the thing people forget to check
diff.filter(d => !/lock|\.min\./.test(d.new_path)).map(d => d.new_path);
```

Useful extras: `/merge_requests/:iid/commits`, `/merge_requests/:iid/notes` (review discussion often
explains *why* something changed), `/repository/files/:path?ref=:branch` to read a whole file.

## GitHub

With the CLI, when the sandbox can reach it:

```bash
gh pr view 205 --json title,body,baseRefName,headRefName,files
gh pr diff 205
```

From the browser, or with a token:

```js
const r = 'owner/repo';
const pr   = await fetch(`https://api.github.com/repos/${r}/pulls/205`,
                         { headers: { Accept: 'application/vnd.github+json' } }).then(r => r.json());
const diff = await fetch(`https://api.github.com/repos/${r}/pulls/205`,
                         { headers: { Accept: 'application/vnd.github.v3.diff' } }).then(r => r.text());
pr.base.ref;   // target branch
```

## Bitbucket

```js
const w = 'workspace', r = 'repo';
const pr   = await fetch(`/2.0/repositories/${w}/${r}/pullrequests/205`).then(r => r.json());
const diff = await fetch(`/2.0/repositories/${w}/${r}/pullrequests/205/diff`).then(r => r.text());
pr.destination.branch.name;
```

## Local clone

If the repo is checked out locally, this is faster and needs no network:

```bash
git fetch origin && git log --oneline origin/<target>..<branch>
git diff origin/<target>...<branch> -- . ':(exclude)*lock*' ':(exclude)*.min.*'
```

---

## What to read, and what to skip

**Read:** the description, the diff hunks, any new constant or allow-list, validation and limits,
new or changed endpoints and payload shapes, and the existing tests (so manual effort goes where
they don't reach).

**Skip:** lockfiles, generated files, minified bundles, snapshot updates, pure formatting commits.

**Always write down:** the target branch, which repos the change spans, and any contract between
two repos (one writes a format, the other renders it). That contract is where the interesting
bugs live, and neither repo's tests cover it.
