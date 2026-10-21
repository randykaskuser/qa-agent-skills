---
name: ui-tour
description: >
  Produce an annotated visual overview of one screen or feature of a web app (or the web part of
  an Electron app) — real screenshots of its key states with numbered pins on every part, a table
  of every control and its choices, the rough edges ranked worst first, and a map of the source
  files behind it — as one self-contained HTML page. Use whenever someone wants to see, understand
  or plan a change to an existing screen before touching it: "screenshot the settings page",
  "show me what the editor's overlay tab looks like", "I want to redesign X, give me context on its
  layout", "what's on this screen and where is it in the code?", "make an overview I can look at",
  "walkthrough of this feature's UI", or a screen name plus "design" or "layout". Also use when a
  previous answer described a UI in text and the user asks for something they can see. Not for
  testing behaviour or writing test cases (use exploratory-web-testing or ticket-driven-qa), and
  not for fully native desktop or mobile apps. Triggers on non-English phrasing too.
license: "MIT"
---

# UI Tour

Turn "I want to change this screen" into a page the person can look at: what is on the screen,
what each part does, what is awkward about it today, and which files to open. The page is the
deliverable. A text description of a UI is not a substitute, because layout problems (a panel
below the fold, an orphaned grid cell, a control far from the one it depends on) are only obvious
when seen.

## What the finished page contains

1. **Annotated screenshots**, one section per key state. Numbered pins mark parts of the screen;
   amber `!` pins mark rough edges. Each pin has a legend entry beside the shot.
2. **Every control**: name, the choices it offers, and notes (which variants it applies to, what
   disables it, limits such as a character cap).
3. **Rough edges**, ranked by how much they get in the way, each with a one-line idea for a fix.
   Ideas are starting points; the person deciding the redesign is the user, not you.
4. **Where it lives in code**: a small tree of the files and the key constants or helpers.

`scripts/build_tour.py` renders all of that from a JSON spec, so every tour looks the same and you
spend the time on observation rather than on HTML.

## Phase 0 — Project notes

Look for `.claude/ui-tour.md` in the project. If it exists, read it: it says how to start the app,
which test data to use, how to reach screens, and what must never be touched. If it does not
exist, you will work these out in Phase 2 and write them there at the end (template:
`references/project-notes.template.md`). Saving them is what makes the second tour in a project
take minutes instead of a discovery session.

Two rules hold regardless of the notes:

- **Never kill processes by name.** The user's own installed copy of the app often shares process
  names with the dev build. Record the PIDs you start and stop only those.
- **Leave the data as you found it.** Toggling a switch to show a state is fine; saving, rendering,
  publishing or deleting is not. Discard unsaved changes when you leave the screen.

## Phase 1 — Read the code first

Find the components behind the screen before opening a browser. Search for the visible labels
(the tab name, a button's text, an i18n key), then read the screen's top component and the pieces
it renders. Note:

- the layout containers (fixed widths, scroll areas, breakpoints) — they explain what you will see;
- every control, its options and what disables it — this fills the controls table;
- default values and limits (max items, max characters);
- where the preview or rendered output comes from.

This is what keeps the annotations true. A pin that says "Padding — disabled for Outline style"
comes from the code, not from guessing at a greyed-out slider.

## Phase 2 — Open the real screen

1. Start the app the way the project notes say. Without notes: read `package.json` scripts, the
   README and any CLAUDE.md/AGENTS.md for the dev command; a backend may need its own process.
   Prefer a port that is free; check before starting. Wait for a ready signal, not a fixed sleep.
2. Use realistic data. A screen rendered against an empty account hides most of its layout. Open
   an existing record that exercises the feature (a finished job, a filled form, a populated
   list). If none exists and creating one would write real data, ask.
3. Drive the browser with the Playwright MCP (or whatever browser tool is available). Use the
   accessibility snapshot to find and click controls; use screenshots for what you show.
4. Use a desktop viewport (1440×900 unless the notes say otherwise). Decide on a phone view now,
   not after the tour is built (see Phase 3).

If the app needs a login, the user signs in themselves in the browser. Never ask for credentials
in chat.

## Phase 3 — Capture the states that matter

Usually two to four shots:

- the screen as it first opens;
- an item selected or a section expanded, so the detail panel is visible;
- anything below the fold or inside a scroll area, scrolled into view (scroll the container with
  `element.scrollTop`, not the page);
- an empty, error or disabled state when it looks noticeably different;
- **a phone-width view (390×844)** when people are likely to open the screen on a phone: public
  pages, landing pages, guides and help pages, anything reached from an email or a shared link,
  and any page whose CSS has breakpoints that change the layout. Skip it for screens that only
  exist inside a desktop app or an admin tool used at a desk. When unsure, take it: a redesign
  that only considered the desktop view is the costly mistake. Resize back to desktop afterwards.

Do not screenshot every state; the page gets long and the person stops reading. Pick the ones a
redesign would touch.

Save shots inside the browser tool's allowed folder, then copy them to a working folder outside
the repository (the system temp folder is fine). Screenshots of real data must never be committed
to a repository unless the user asks.

Some screens are not reachable through the dev web server (an Electron splash, a native dialog).
For those, take a screenshot of the real window by its process id and say in the page that it was
captured differently.

## Phase 4 — Observe, then write the spec

Look at each screenshot and decide the pins. Read pin coordinates in the **full** screenshot's
pixels; give the shot a `crop` box that frames just the screen (a dialog, a page body), and the
script re-maps the pins. Put a pin on the element itself, not on empty space next to it.

**Parts** (numbered): one per region or control group a designer would talk about. Keep each shot
to **ten pins at most**, parts and rough edges together. Past ten the pins cover the screen they
are meant to explain and the legend becomes a wall of text nobody reads. Group small controls
under one pin ("Row switch and ⋮ menu", "Quick settings: preset, layout, clips, duration"), and
if a screen genuinely has more to say, split it into two shots with tighter crops. The build
script warns when a shot goes over the limit.

**Rough edges** (amber): things that get in the way of using or reading the screen. Look for:

- content that needs scrolling to reach after an action (settings appearing below the fold);
- the same value shown two ways (`1:53` in one place, `113.08` in another);
- theme leaks (a light native scrollbar in a dark UI, unstyled form controls);
- grid imbalance (one field alone in a two-column row), related controls far apart;
- weak states (selection barely visible, disabled looking the same as off);
- labels that no longer match what the section contains.

Rank them by impact, not by order found. State each as what you saw, with the evidence (sizes,
values, text), then one idea. Don't pad the list: three real issues beat eight cosmetic ones.

Write the spec (see "The tour spec" below) next to the screenshots and run:

```bash
python scripts/build_tour.py <workdir>/tour.json <workdir>/<screen>-tour.html
```

The script warns when a pin falls outside its cropped shot or points at a rough edge that does not
exist. Fix those before going on.

## Phase 5 — Check, deliver, clean up

1. Open the page once in the browser and look at it: pins on their targets, nothing clipped,
   legend matching the pins. One pass of fixes, no more.
2. Deliver it: publish it as an artifact or page if the environment offers that, otherwise open
   the HTML file for the user and give its path. The page is a single file with the images
   embedded, so it can be sent as-is.
3. Clean up: discard unsaved edits in the app, stop the servers you started by PID, delete stray
   screenshots from inside the repository.
4. Write or update `.claude/ui-tour.md` with anything you had to work out (start command, ports,
   the URL of a good example record, gotchas). Date it.

Tell the user, in a few lines: where the page is, the top two or three rough edges, and one
question about what they want to change next.

## The tour spec

```json
{
  "title": "Overlay Tab Map",
  "eyebrow": "Clip Editor · Edit clip → Overlay",
  "heading": "What the Overlay tab looks like today",
  "intro": "Dev build at 1440×900, a finished job with three clips.",
  "accent": "#7FA300",
  "shots": [
    {
      "image": "overlay-selected.png",
      "crop": [208, 90, 1024, 720],
      "title": "List and preview",
      "caption": "Clip label switched on and selected.",
      "pins": [
        {"x": 464, "y": 390, "title": "Video preview", "note": "Overlays drawn at the playhead."},
        {"x": 1183, "y": 410, "kind": "issue", "issue": 3, "title": "Light scrollbar"}
      ]
    }
  ],
  "controls_intro": "What a text overlay can be set to today.",
  "controls": [
    {"name": "Style", "choices": ["Label", "Caps", "Outline"], "note": "Text overlays only."}
  ],
  "issues": [
    {"title": "Settings out of sight", "detail": "913 px of content in a 459 px area; selecting a row does not scroll.", "idea": "Show settings inline under the selected row."}
  ],
  "code_intro": "All under web/src/components/.",
  "code_map": ["ClipEditorModal.tsx  dialog\n└─ overlays/OverlayTab.tsx\n   ├─ OverlayRow.tsx\n   └─ OverlaySettings.tsx"],
  "footer": "Captured 2026-10-21 from the dev build. Nothing was saved."
}
```

- `image` paths are relative to the spec file. `crop` is `[x, y, width, height]` in screenshot
  pixels; omit it to use the whole image.
- Pins: `x`/`y` in full-screenshot pixels; `kind: "issue"` plus `issue` (1-based rank, or the
  issue's `id`) for a rough edge; anything else is a numbered part.
- `accent` should be the product's own accent colour so the page feels like it belongs to the app.
- `code_map` is a list of plain-text blocks shown side by side.
- Cropping needs Pillow (`pip install pillow`). Without it the script embeds the full image and
  the pins still land correctly.

## Words on the page

Write for the person who will redesign the screen: name things by their visible labels, keep
notes to one sentence, give numbers where you have them. Write the page in the language the user
writes to you in, but keep the app's own labels exactly as the UI shows them.
