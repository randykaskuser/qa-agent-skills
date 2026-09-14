# Standard checks

Pull in whichever apply to the change. Each list came from a real run; the notes say what it caught.

## Rendered content (consumer page)

- Computed styles per element: `getComputedStyle` for size, weight, list-style, decoration.
- Links: `target` and `rel`.
- Dark and light theme. Some surfaces are locked to one theme — say so rather than skipping silently.
- Width 375px with a **long unbroken URL or word**. Check that
  `document.documentElement.scrollWidth > window.innerWidth` is false.
  *This found a real horizontal-overflow bug.*

## Stored HTML / rich text

Set the value through the API (the editor usually cannot produce these), then check the page.

- Nothing executes and dangerous parts are stripped, for all of:
  `<script>`, `<img src=x onerror=…>`, `<svg onload=…>`, `<iframe>`, `<style>`, `<form>`,
  `onclick` / `style` / `class` attributes, and `javascript:` / `data:` hrefs —
  including mixed case and leading whitespace.
- Disallowed tags are stripped but their **text is kept**.
- Empty markup (`<p></p>`, `<p>&nbsp;</p>`) hides the section instead of rendering a gap.

## Edge data

- Empty value.
- Whitespace only.
- `<`, `>`, `&` inside plain text.
- Plain text that *looks like* a tag: `We have <a lot> of fun`.
- Single vs double line breaks.
- Very long content.
- **Clearing a field that had a value.** Check the request actually sends empty or null —
  `value || undefined` silently drops it and the old value survives.

## Image uploads

Generate the files with `__qa.img` rather than hunting for real ones.

- The exact recommended size.
- The minimum size exactly (the boundary).
- Just below the minimum, with the correct ratio.
- Wrong ratio but big enough.
- Wrong ratio *and* too small — expect one combined message, not two dialogs.
- A non-image file.
- A file of roughly 10 MB (`noise: true`).
- For each dialog button, check what is kept afterwards.

## Save flows

- Staged vs persisted: dialog Save vs page Save.
- Close with X, then reopen: is the pending value still there?
- Discard.
- Reload after saving.
- Two records changed in one save.
- A forced upload failure (`__qa.fail`): what was already saved? What does the message say?
- A slow response racing a user action (`__qa.delay`).

## Dirty state

Open the record, change nothing, leave. A guard dialog means something is marked dirty.
Bisect field by field to find which one — it is often a neighbouring feature, not the change
under test.

## Multi-tenant / multi-brand

- The same check on a second tenant that runs a different build.
- A tenant on the production build, read-only, to see whether the bug ships.
- A field that another tool can also edit (legacy admin, back office): does it show or break
  the new value format?
