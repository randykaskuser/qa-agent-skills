#!/usr/bin/env python3
"""Build a single-file, annotated UI tour page from screenshots and a JSON spec.

    python build_tour.py tour.json out.html

The spec is described in SKILL.md ("The tour spec"). Pin coordinates are in the
ORIGINAL screenshot's pixels; when a shot has a `crop`, the script crops the image
and re-maps every pin, so you can read coordinates straight off the full screenshot.

Images are embedded as data: URIs, so the page works offline and can be sent as one
file. Cropping and JPEG re-encoding need Pillow; without it the original image is
embedded uncropped (pins still land correctly) and a warning is printed.

Standard library only, apart from the optional Pillow.
"""
from __future__ import annotations

import base64
import html
import io
import json
import mimetypes
import sys
from pathlib import Path

try:
    from PIL import Image  # type: ignore
except ImportError:  # pragma: no cover - exercised only where Pillow is missing
    Image = None

DEFAULT_ACCENT = "#2F6FEB"
MAX_PINS = 10  # per shot, parts and rough edges together


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def load_image(path: Path, crop):
    """Return (data_uri, width, height, crop_origin) for the image as embedded."""
    if Image is not None:
        im = Image.open(path)
        ox, oy = 0, 0
        if crop:
            x, y, w, h = crop
            im = im.crop((x, y, x + w, y + h))
            ox, oy = x, y
        im = im.convert("RGB")
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=86)
        uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
        return uri, im.width, im.height, (ox, oy)
    if crop:
        print(f"warning: Pillow not installed; {path.name} embedded uncropped", file=sys.stderr)
    data = path.read_bytes()
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    w, h = _png_size(data) if mime == "image/png" else (None, None)
    if w is None:
        raise SystemExit(f"{path}: install Pillow to read the size of non-PNG images")
    return f"data:{mime};base64," + base64.b64encode(data).decode(), w, h, (0, 0)


def _png_size(data: bytes):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None, None
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def build(spec: dict, base: Path) -> str:
    accent = spec.get("accent") or DEFAULT_ACCENT
    shots_html = []
    issue_ids = {str(i.get("id", n + 1)) for n, i in enumerate(spec.get("issues", []))}
    for si, shot in enumerate(spec.get("shots", [])):
        path = (base / shot["image"]).resolve()
        uri, w, h, (ox, oy) = load_image(path, shot.get("crop"))
        pins, legend = [], []
        part_no = 0
        if len(shot.get("pins", [])) > MAX_PINS:
            print(f"warning: shot {si + 1} ('{shot.get('title', '')}') has {len(shot['pins'])} pins; "
                  f"more than {MAX_PINS} crowds the image. Group small controls or split the shot.", file=sys.stderr)
        for pi, pin in enumerate(shot.get("pins", [])):
            key = f"s{si}p{pi}"
            is_issue = pin.get("kind") == "issue"
            if is_issue:
                ref = str(pin.get("issue", ""))
                label = "!"
                if ref and ref not in issue_ids:
                    print(f"warning: pin '{pin.get('title')}' points at unknown issue {ref}", file=sys.stderr)
            else:
                part_no += 1
                label = str(part_no)
            left = (pin["x"] - ox) / w * 100
            top = (pin["y"] - oy) / h * 100
            if not (0 <= left <= 100 and 0 <= top <= 100):
                print(f"warning: pin '{pin.get('title')}' falls outside shot {si + 1} after cropping", file=sys.stderr)
            cls = "pin issue" if is_issue else "pin"
            pins.append(
                f'<button class="{cls}" style="left:{left:.2f}%;top:{top:.2f}%" data-k="{key}" '
                f'aria-label="{esc(pin.get("title"))}">{label}</button>'
            )
            note = pin.get("note", "")
            if is_issue and pin.get("issue"):
                note = (note + " " if note else "") + f"See rough edge #{pin['issue']}."
            li_class = ' class="issue"' if is_issue else ""
            legend.append(
                f'<li data-k="{key}"{li_class}><span class="tag">{label}</span>'
                f'<div><b>{esc(pin.get("title"))}</b><small>{esc(note)}</small></div></li>'
            )
        shots_html.append(f"""
  <section>
    <div class="sec-head"><h2>{esc(shot.get("title", f"View {si + 1}"))}</h2>
      {f'<p class="lede">{esc(shot["caption"])}</p>' if shot.get("caption") else ""}</div>
    <div class="figure" data-fig>
      <div class="shot"><img src="{uri}" alt="{esc(shot.get("alt") or shot.get("title", "Screenshot"))}" width="{w}" height="{h}">
        {"".join(pins)}
      </div>
      <ol class="legend">{"".join(legend)}</ol>
    </div>
  </section>""")

    controls = spec.get("controls", [])
    controls_html = ""
    if controls:
        rows = "".join(
            f'<tr><td class="name">{esc(c.get("name"))}</td><td><div class="chips">'
            + "".join(f'<span class="chip">{esc(x)}</span>' for x in c.get("choices", []))
            + f'</div></td><td class="note">{esc(c.get("note"))}</td></tr>'
            for c in controls
        )
        controls_html = f"""
  <section>
    <div class="sec-head"><h2>Every control</h2>
      {f'<p class="lede">{esc(spec["controls_intro"])}</p>' if spec.get("controls_intro") else ""}</div>
    <div class="table-wrap"><table><thead><tr><th>Control</th><th>Choices</th><th>Notes</th></tr></thead>
      <tbody>{rows}</tbody></table></div>
  </section>"""

    issues = spec.get("issues", [])
    issues_html = ""
    if issues:
        cards = "".join(
            f'<article class="issue-card"><h3><span class="tag issue">{esc(i.get("id", n + 1))}</span>{esc(i.get("title"))}</h3>'
            f'<p>{esc(i.get("detail"))}</p>'
            + (f'<p class="fix">{esc(i["idea"])}</p>' if i.get("idea") else "")
            + "</article>"
            for n, i in enumerate(issues)
        )
        issues_html = f"""
  <section>
    <div class="sec-head"><h2>Rough edges</h2><p class="lede">Ranked by how much they get in the way. Ideas are starting points, not decisions.</p></div>
    <div class="issues">{cards}</div>
  </section>"""

    code = spec.get("code_map")
    code_html = ""
    if code:
        blocks = code if isinstance(code, list) else [code]
        code_html = f"""
  <section>
    <div class="sec-head"><h2>Where it lives in code</h2>
      {f'<p class="lede">{esc(spec["code_intro"])}</p>' if spec.get("code_intro") else ""}</div>
    <div class="cols">{"".join(f'<div class="tree">{esc(b)}</div>' for b in blocks)}</div>
  </section>"""

    footer = f'<footer>{esc(spec["footer"])}</footer>' if spec.get("footer") else ""
    return TEMPLATE.format(
        title=esc(spec.get("title", "UI Tour")),
        eyebrow=esc(spec.get("eyebrow", "")),
        heading=esc(spec.get("heading", spec.get("title", "UI Tour"))),
        intro=esc(spec.get("intro", "")),
        accent=esc(accent),
        body="".join(shots_html) + controls_html + issues_html + code_html,
        footer=footer,
    )


TEMPLATE = """<meta charset="utf-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* Layout: annotated screenshots first, then the control reference, rough edges and code map. */
:root {{
  --bg: #F5F6F8; --surface: #FFFFFF; --line: #D9DDE3; --fg: #15181D; --muted: #5B6270;
  --accent: {accent}; --accent-ink: #FFFFFF; --warn: #D98400; --warn-ink: #1A1100;
  --body: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono: ui-monospace, "Cascadia Code", "SF Mono", Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #0F1114; --surface: #171A1F; --line: #2A2F37; --fg: #E8EAEE; --muted: #9AA1AD;
  --warn: #F2A93B; color-scheme: dark; }} }}
:root[data-theme="dark"] {{ --bg: #0F1114; --surface: #171A1F; --line: #2A2F37; --fg: #E8EAEE; --muted: #9AA1AD;
  --warn: #F2A93B; color-scheme: dark; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--fg); font: 15px/1.55 var(--body);
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 40px 64px; }}
.wrap {{ max-width: 1120px; margin: 0 auto; display: flex; flex-direction: column; gap: 52px; }}
header {{ display: flex; flex-direction: column; gap: 10px; max-width: 72ch; }}
.eyebrow {{ font: 12px var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }}
h1 {{ font-size: clamp(28px, 4.6vw, 42px); line-height: 1.08; margin: 0; text-wrap: balance; letter-spacing: -.01em; }}
h2 {{ font-size: 22px; margin: 0; text-wrap: balance; }}
p {{ margin: 0; }}
.lede {{ color: var(--muted); }}
section {{ display: flex; flex-direction: column; gap: 18px; }}
.sec-head {{ display: flex; flex-direction: column; gap: 6px; max-width: 72ch; }}
.key {{ display: flex; gap: 18px; flex-wrap: wrap; font-size: 13px; color: var(--muted); }}
.key > span {{ display: inline-flex; align-items: center; gap: 8px; }}
.figure {{ display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(0, 1fr); gap: 24px; align-items: start; }}
@media (max-width: 860px) {{ .figure {{ grid-template-columns: minmax(0, 1fr); }} }}
.shot {{ position: relative; border: 1px solid var(--line); border-radius: 10px; overflow: hidden; background: var(--surface); }}
.shot img {{ display: block; width: 100%; height: auto; max-width: 100%; }}
.pin {{ position: absolute; transform: translate(-50%, -50%); width: 26px; height: 26px; border-radius: 50%;
  border: 2px solid var(--surface); background: var(--accent); color: var(--accent-ink); font: 600 12px/22px var(--mono);
  text-align: center; cursor: pointer; padding: 0; box-shadow: 0 0 0 1px var(--accent), 0 2px 6px rgba(0,0,0,.35); transition: transform .15s ease; }}
.pin.issue {{ background: var(--warn); color: var(--warn-ink); box-shadow: 0 0 0 1px var(--warn), 0 2px 6px rgba(0,0,0,.35); border-radius: 6px; }}
.pin.on, .pin:focus-visible {{ transform: translate(-50%, -50%) scale(1.35); outline: none; z-index: 2; }}
@media (max-width: 520px) {{ .pin {{ width: 20px; height: 20px; font-size: 10px; line-height: 16px; }} }}
.legend {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 2px; }}
.legend li {{ display: grid; grid-template-columns: 28px minmax(0, 1fr); gap: 10px; padding: 9px 10px; border-radius: 8px; border: 1px solid transparent; }}
.legend li.on {{ background: var(--surface); border-color: var(--line); }}
.tag {{ display: inline-block; font: 600 12px/24px var(--mono); width: 24px; height: 24px; text-align: center; border-radius: 50%;
  background: var(--accent); color: var(--accent-ink); flex: none; }}
.issue .tag, .tag.issue {{ background: var(--warn); color: var(--warn-ink); border-radius: 6px; }}
.legend b {{ font-weight: 600; display: block; }}
.legend small {{ color: var(--muted); font-size: 13px; display: block; }}
.table-wrap {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; }}
table {{ border-collapse: collapse; width: 100%; min-width: 600px; font-size: 14px; }}
th, td {{ text-align: left; padding: 11px 14px; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{ font: 500 12px var(--mono); text-transform: uppercase; letter-spacing: .06em; color: var(--muted); background: var(--surface); }}
tr:last-child td {{ border-bottom: 0; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.chip {{ font: 12px var(--mono); border: 1px solid var(--line); border-radius: 4px; padding: 1px 7px; white-space: nowrap; }}
td.name {{ font-weight: 600; }}
td.note {{ color: var(--muted); font-size: 13px; }}
.issues {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 320px), 1fr)); gap: 14px; }}
.issue-card {{ border: 1px solid var(--line); border-left: 3px solid var(--warn); border-radius: 0 10px 10px 0; padding: 16px 18px;
  display: flex; flex-direction: column; gap: 8px; background: var(--surface); }}
.issue-card h3 {{ margin: 0; font-size: 16px; display: flex; gap: 10px; align-items: center; }}
.issue-card p {{ color: var(--muted); font-size: 14px; }}
.issue-card .fix {{ color: var(--fg); }}
.issue-card .fix::before {{ content: "Idea: "; font: 12px var(--mono); color: var(--muted); }}
.cols {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 380px), 1fr)); gap: 20px; }}
.tree {{ font: 13px/1.8 var(--mono); background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
  padding: 16px 18px; overflow-x: auto; white-space: pre; }}
footer {{ color: var(--muted); font-size: 13px; border-top: 1px solid var(--line); padding-top: 16px; }}
@media (prefers-reduced-motion: reduce) {{ .pin {{ transition: none; }} }}
</style>
<div class="wrap">
  <header>
    <div class="eyebrow">{eyebrow}</div>
    <h1>{heading}</h1>
    <p class="lede">{intro}</p>
    <div class="key"><span><span class="tag">1</span> part of the screen</span><span><span class="tag issue">!</span> rough edge</span></div>
  </header>
  {body}
  {footer}
</div>
<script>
document.querySelectorAll('[data-fig]').forEach(function (fig) {{
  function set(k, on) {{ fig.querySelectorAll('[data-k="' + k + '"]').forEach(function (el) {{ el.classList.toggle('on', on); }}); }}
  fig.querySelectorAll('[data-k]').forEach(function (el) {{
    var k = el.getAttribute('data-k');
    ['mouseenter', 'focus'].forEach(function (e) {{ el.addEventListener(e, function () {{ set(k, true); }}); }});
    ['mouseleave', 'blur'].forEach(function (e) {{ el.addEventListener(e, function () {{ set(k, false); }}); }});
  }});
}});
</script>
"""


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    spec_path, out = Path(argv[1]), Path(argv[2])
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    page = build(spec, spec_path.parent)
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out} ({len(page) / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
