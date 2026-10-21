# UI tour notes — template

Copy this file to `.claude/ui-tour.md` in the project and fill it in. The `ui-tour` skill reads it
before every tour and adds to it after one. Date every fact; re-check anything that looks off.

> No credentials, tokens or customer data here. Commands, ports and record IDs are fine.

---

## Verified on: <YYYY-MM-DD> by <who>

## Start the app

| Process | Command (from repo root) | Port | Ready when |
|---|---|---|---|
| Backend | `<e.g. cd backend && .venv/bin/python -m uvicorn api:app --port 8000>` | 8000 | `<GET /api/health returns 200>` |
| Frontend | `<e.g. cd web && npm run dev>` | 3000 | `<"Ready in" in the log>` |

Notes: <env files it reads, data directory it shares with an installed copy, anything that must be
running first>

## Never touch

- Processes: <names the user's own installed app uses — stop only the PIDs you started>
- Data: <records, accounts or folders that must not be modified>
- Actions: <buttons that publish, bill, email or render for real>

## Good example data

| Screen | URL or path to reach it | Why this record |
|---|---|---|
| <Clip editor> | `<http://localhost:3000/job?id=…>` → <Edit on clip 1> | <finished job with 3 clips and captions> |

## Screens toured

| Date | Screen | Page |
|---|---|---|
| <YYYY-MM-DD> | <Edit clip → Overlay> | <path to the HTML, if kept> |

## Gotchas

- <e.g. the browser tool can only write screenshots under the repo; copy them out and delete them>
- <e.g. closing the editor with changes asks "Discard changes?" — choose Discard>
