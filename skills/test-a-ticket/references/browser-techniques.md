# Browser techniques

## Driving the browser

- **Pick one browser and stay in it.** Switch only when you need something it cannot do —
  typically saving a screenshot to disk for a bug attachment. If the browser drops mid-run, its
  tools usually come back within a minute: wait and retry before switching.
- **Never trigger native `alert` / `confirm` / `beforeunload` dialogs.** They freeze browser
  automation. In-app guard dialogs are fine — close them with their own Cancel button.
- **Read the page with DOM/JS.** Take screenshots only when layout is the question, or as bug evidence.
- **Clicking reliably.**
  - Get coordinates from `getBoundingClientRect()`, `scrollIntoView()` first, then click.
  - JS `.click()` works on plain buttons but often not on headless-UI-style triggers
    (dropdowns, popovers, custom comboboxes). If nothing happens, use a real pointer click.
  - Keep emulated viewports **no wider than the visible pane**. Scaled-down viewports make clicks miss.
  - Dropdowns and dialogs move when their content changes. Re-read the trigger's rect before
    every click, and read option positions from `[role="option"]` after opening.
  - After a click that should open something, **verify with the DOM before continuing.**
    A silent miss makes every later step wrong.
- **Selecting text.** Keyboard selection with modifier keys is unreliable inside automated
  browsers, especially on macOS. Use a triple click for a paragraph, or set the input's value
  directly through the form-input tool.
- **Rich-text editor input rules** (TipTap / ProseMirror / Quill): type the trigger by itself
  (`## `, `- `, `1. `, `> `) and then the text. One long typed string will not trigger them.
  Auto-link needs the trailing space typed on its own.
- **Unsaved-changes guards.** Test "dirty on open" by clicking an in-app link and checking for
  the guard dialog, then press Cancel.

## When behaviour is unclear, read the code that is running

- **Find endpoints.** Grep the loaded JS chunks for the API client or the route. Server-rendered
  pages may never show the data request in the network log.
- **Find the logic.** Search the minified bundle for field names (`_description`, `isDirty`) to see
  what is compared or sent. Two things this reliably finds: a dirty check's field list, and a
  payload builder that drops empty values.
- **Copy a flow through the API** when a test needs several records — for example
  presign → upload with the returned fields → PATCH. Say in the report that you did this.
- **Open a failing asset URL directly** to read the server's error body. CDN and signing errors
  are usually explicit there and invisible in the page.
- **Toasts disappear in seconds.** Start `__qa.watch()` *before* the action that triggers them.

## Helpers

The helper script is `scripts/browser-helpers.js` in this skill's folder. Read it and paste the
full contents into the browser's JavaScript tool on the page under test. **Reinstall after every
navigation or reload.**

What it gives you on `window.__qa`:

| Helper | Use |
|---|---|
| `reqs` | Log of non-GET requests (plus GETs matching `logGet`), with bodies and status |
| `logGet` | RegExp of GET URLs worth logging — set it to your project's interesting routes |
| `fail` | Set to a RegExp to make matching requests fail (error-path tests) |
| `delay` | `{ re, ms }` to slow matching requests (race tests) |
| `img(w, h, name, opts)` | Generate a test image file (any size/type; `noise: true` for ~10 MB) |
| `setFile(input, file)` | Put a file into a file input and fire `change` |
| `paste(el, html, text)` | Simulate pasting rich HTML into an editor |
| `og(path)` | Read og tags of a share page and check the image really loads |
| `watch(re)` | Capture short-lived toasts and messages; returns a stop function |

Usage:

```js
window.__qa.reqs.length = 0;                                  // before an action
window.__qa.reqs;                                             // after it
window.__qa.fail = /amazonaws\.com|\/upload/;                 // force upload failures
window.__qa.delay = { re: /\/api\/.*\/config/, ms: 4000 };    // race a slow response
window.__qa.fail = null; window.__qa.delay = null;            // always reset afterwards

const file = await window.__qa.img(1200, 630, 'og.png');
window.__qa.setFile(document.querySelector('input[type=file]'), file);
```

The OS file picker cannot be driven — always inject files this way.
