# Environment map — template

Copy this file to `environment-map.md` in the same folder and fill it in for your project.
Keep it current: re-verify when something looks off, and update it the moment it changes.
Date every fact. A stale environment map costs more time than no map at all.

> Do not commit real credentials, tokens or customer data here. Hostnames, IDs and
> endpoint shapes are fine; secrets are not.

---

## Verified on: <YYYY-MM-DD> by <who>

## Source surface (admin / dashboard / CMS)

| Environment | URL | Notes |
|---|---|---|
| Test | `https://…` | stack/framework, anything unusual |
| Production | `https://…` | **read-only, always.** Its build can lag — check the bundle before assuming |

**Internal API:** base path, auth mechanism (cookie / bearer / JWT and where the token lives),
and the handful of paths you actually use:

```
GET|PATCH  /api/…/{id}/         fields: …
POST       /api/…/{id}/duplicate/
POST       /api/…/generate-presigned-url/
```

## Consumer surfaces

| Surface | Environment | URL | Which backend it talks to |
|---|---|---|---|
| Public web app | staging | `https://…` | test API |
| Public web app | production | `https://…` | production API |
| Public API (what the mobile apps read) | test | `https://…/api/v…/…` | — |
| Share / preview pages | — | `https://<domain>/s/<type>-<id>/` | server-rendered og tags |

**How to tell which backend you are really on:** read
`performance.getEntriesByType('resource')` on the page and look at the API host.

## IDs and tenants

| Name | ID | Use |
|---|---|---|
| Reference / internal tenant | `…` | safe to write to |
| Client tenant | `…` | **never write** |

Always set the tenant explicitly in the URL (for example `?appId=…`). Pages remember the
last selection in local storage, and that may be a real client's data.

## Assets and CDN

- CDN hosts: `…`
- Signed URLs? If yes, an unsigned URL fails with a specific error body — record it here.
  **Always load image URLs found in og tags; don't just check that the tag exists.**
- Upload bucket / presign behaviour (does it de-duplicate file names?).

## Reachability

- Can the agent sandbox reach the forge and the app hosts directly, or must everything
  go through the user's logged-in browser? Record which, and any bot check that gets in the way.

## Known gotchas

One line each. This section pays for the whole file. Examples of the kind of thing that belongs here:

- A page or dialog that only **stages** changes — a separate page-level Save persists them, and Discard reverts.
- A field that always marks the form dirty on open, so "unsaved changes" is pre-existing noise.
- An icon that looks like a close button but is actually destructive — say how to target the real one.
- A length limit on a name field that is not shown in the UI.
- New records landing in a hidden state by default.
- A second legacy page with the same save logic that also needs checking.
- A surface that is dark-only or light-only, so one theme cannot be tested there.
