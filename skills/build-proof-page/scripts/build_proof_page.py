#!/usr/bin/env python3
"""Build a QA proof page: one light-theme HTML file, images embedded.

  python3 build_proof_page.py spec.json out.html [--png]

--png also writes <id>-before-after.png (and .html) per retest ticket next to out.html, for
pasting into a tracker comment. Needs Pillow and Chrome or Chromium (set CHROME to its path if not found).

Image paths are relative to spec.json. A working spec: spec.example.json next to this script.

Spec (* = required):
  title*, lead* (verdict first), eyebrow
  columns*      what is compared: platforms, environments, users, layers, or ["Result"]
                ("platforms" also works)
  rows*         [{item*, cells*: [[cls, text], ...] one per column, source, ticket}]
                  ok matches / passed      d differs from the source    x failed
                  o  odd one out, no source  b blocked, partial, not run  n observed without a source, or not applicable
                  a row with a d or x cell needs source (the mock, criterion or code it breaks)
  stats         [{label, value, note}] or [{label, count: cls, note}]; count is the number of rows
                whose worst cell is cls (x, d, b, o, ok, n), so totals cannot disagree with the table. "3 / 4" or "3 of 4" draws a bar.
  rule          {title, items[]}: what was judged against
  tickets       [{id, title, note, url}]; url only when you know it
  figures       [{title*, why*, date* (with build or environment), image or evidence* (literal text),
                  evidence may be text or a list of lines; subtitle, tested[] (records used), severity, steps[], expected, actual, tickets}]
                a failed or differing row needs at least one figure in the page
  table         {heading, columns[], rows[[...]]}: everything that was tested
  open          [text]: blocked items, gaps, test data left behind
  headings      {tickets, rows, retest, figures, open}: rename a section
  legend        {cls: wording}: reword a class, e.g. {"ok": "confirmed", "b": "question", "x": "anomaly"}

Fix retest (before/after) — add retest; title, lead, columns and rows may then be left out:
  retest        [{id*, title* (one line), sub* (environment, date, viewer/event timezones when they matter),
                  comment (the one-line tracker comment that goes with the PNG),
                  checks*: [{check*, before*, after*, before_image, after_image}]}]
                before_image: crop of the original bug-report proof (red border); after_image: crop of the retest (green border)
                for passed retests only; a fix that still fails is a ticket-test row with a figure

Text is escaped; <strong>, <em>, <code>, <br> and <a href="http..."> are kept.
"""
import base64, html, json, mimetypes, os, re, shutil, subprocess, sys

CSS = '''
:root{--bg:#f3f4f8;--surface:#ffffff;--surface2:#f8f9fc;--fg:#12161d;--muted:#566070;--line:#dfe3ea;--accent:#2155d6;--accent-bg:#e8eefc;
--ok:#12703f;--ok-bg:#e3f5ea;--bad:#b42318;--bad-bg:#fdeceb;--warn:#8a5a00;--warn-bg:#fff3d3;--shadow:0 1px 2px rgba(16,24,40,.06),0 4px 14px rgba(16,24,40,.05);
color-scheme:light;--display:"Space Grotesk",system-ui,sans-serif;--body:"Inter",system-ui,sans-serif}
html{scroll-behavior:smooth;scroll-padding-top:72px}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:15px;line-height:1.6}
h1,h2,h3{font-family:var(--display);margin:0;text-wrap:balance;letter-spacing:-.01em}
h1{font-size:34px;line-height:1.15;font-weight:600}
h2{font-size:22px;font-weight:600}
h3{font-size:16px;font-weight:600}
p{margin:0}a{color:var(--accent)}
.muted{color:var(--muted)}
.nav{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:30;background:var(--bg)}
.nav-in{max-width:1080px;margin:0 auto;display:flex;gap:4px;overflow-x:auto;padding:8px max(16px,env(safe-area-inset-right,0px)) 8px max(16px,env(safe-area-inset-left,0px));scrollbar-width:none}
.nav a{white-space:nowrap;text-decoration:none;color:var(--muted);font-weight:500;font-size:14px;padding:6px 12px;border-radius:999px}
.nav a:hover{background:var(--accent-bg);color:var(--accent)}
.wrap{max-width:1080px;margin:0 auto;padding-block:28px 72px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:44px}
section{display:grid;gap:16px;min-width:0}
.eyebrow{font-size:12px;letter-spacing:.09em;text-transform:uppercase;color:var(--accent);font-weight:600;margin-bottom:8px}
.hero{display:grid;gap:18px}
.hero p.lead{max-width:62ch;color:var(--muted);font-size:16px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.stat{padding:16px;display:grid;gap:8px;align-content:start}
.stat b{font-family:var(--display);font-size:26px;font-weight:600}
.bar{height:8px;border-radius:99px;background:var(--line);overflow:hidden}.bar i{display:block;height:100%;background:var(--ok);border-radius:99px}.bar i.part{background:var(--warn)}
.rule{padding:16px 18px;display:grid;gap:6px;border-left:4px solid var(--accent)}
.rule ul{margin:0;padding-left:18px;display:grid;gap:4px}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.tkt{padding:16px;display:grid;gap:6px;text-decoration:none;color:inherit}
.tkt:hover{border-color:var(--accent)}
.tkt .id{font-family:var(--display);font-weight:600;color:var(--accent)}
.tkt .cnt{font-size:13px;color:var(--muted)}
.tbl{border:1px solid var(--line);border-radius:14px;background:var(--surface);box-shadow:var(--shadow)}
table{width:100%;border-collapse:separate;border-spacing:0;font-size:14px;min-width:760px}
th,td{text-align:left;padding:11px 14px;border-bottom:1px solid var(--line);vertical-align:top}
thead th{position:sticky;top:calc(env(safe-area-inset-top,0px) + 53px);z-index:5;background:var(--surface2);font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:600;white-space:nowrap}
tbody th{font-weight:600;background:var(--surface);min-width:150px}
tbody tr:last-child>*{border-bottom:0}
tbody tr:hover>*{background:var(--surface2)}
td.ok{background:var(--ok-bg)}td.d,td.x{background:var(--bad-bg)}td.o,td.b{background:var(--warn-bg)}td.n{background:transparent}
td.ok::before,td.d::before,td.x::before,td.o::before,td.b::before{display:inline-block;margin-right:6px;font-weight:700}
td.ok::before{content:"✓";color:var(--ok)}td.d::before{content:"≠";color:var(--bad)}td.x::before{content:"✗";color:var(--bad)}td.o::before{content:"~";color:var(--warn)}td.b::before{content:"!";color:var(--warn)}
.src{display:block;font-weight:400;font-size:12.5px;color:var(--muted)}
td.tk{color:var(--muted);font-size:13px;white-space:nowrap}
td.num{color:var(--muted);font-variant-numeric:tabular-nums}
.legend{display:flex;flex-wrap:wrap;gap:8px 16px;font-size:13px;color:var(--muted)}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:-1px}
.pill{display:inline-block;font-size:12px;font-weight:600;padding:2px 10px;border-radius:999px}
.pill.ok{background:var(--ok-bg);color:var(--ok)}
.chips{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-top:8px}
.chip{font-size:12.5px;font-weight:500;background:var(--accent-bg);color:var(--accent);padding:3px 10px;border-radius:999px}
.lbl{font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);font-weight:600;margin-right:2px}
.figs{display:grid;gap:18px}
.fig{margin:0;padding:18px;display:grid;gap:14px}
.fig figcaption{display:flex;gap:14px;align-items:flex-start}
.fig .num{flex:none;width:30px;height:30px;border-radius:50%;background:var(--accent);color:#fff;display:grid;place-items:center;font-weight:600;font-size:14px}
.fig .why{margin-top:10px;max-width:75ch}
.fig dl{margin:10px 0 0;display:grid;grid-template-columns:max-content 1fr;gap:4px 12px;max-width:80ch}.fig dt{color:var(--muted);font-size:13px}.fig dd{margin:0;overflow-wrap:anywhere}.fig dd ol{margin:0;padding-left:18px}.fig pre{margin:0;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:var(--surface2);font-size:13px;white-space:pre-wrap;overflow-wrap:anywhere}
.fig .tk{margin-top:4px;font-size:13px;color:var(--muted)}
.zoom{all:unset;display:block;cursor:zoom-in;border-radius:10px;overflow-x:auto}
.zoom:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
.zoom img{display:block;width:100%;min-width:620px;border:1px solid var(--line);border-radius:10px}
.lb{position:fixed;inset:0;z-index:100;background:rgba(10,12,16,.86);display:none;overflow:auto;padding:24px;cursor:zoom-out}
.lb.on{display:block}.lb img{display:block;margin:auto;max-width:none;width:min(1500px,200vw);border-radius:8px}
.filter{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.filter input{font:inherit;padding:9px 12px;border-radius:10px;border:1px solid var(--line);background:var(--surface);color:var(--fg);min-width:min(260px,100%)}
.notes{padding:18px 20px;display:grid;gap:10px}
.notes ul{margin:0;padding-left:20px;display:grid;gap:6px}
.blk{background:var(--warn-bg);color:var(--warn);border-radius:10px;padding:10px 14px;font-weight:500}
@media (max-width:900px){.tbl{overflow-x:auto;-webkit-overflow-scrolling:touch}thead th{position:static}}
@media (max-width:640px){h1{font-size:27px}.fig{padding:14px}}
'''

CLS = {"ok": "matches", "d": "differs from the source", "x": "failed", "o": "differs from the others, no source",
       "b": "blocked, partial or not run", "n": "observed without a source, or not applicable"}
WORST = ("x", "d", "b", "o", "ok", "n")  # a row counts as its worst cell
SW = {"ok": ("ok-bg", "ok"), "d": ("bad-bg", "bad"), "x": ("bad-bg", "bad"), "o": ("warn-bg", "warn"), "b": ("warn-bg", "warn"), "n": ("surface", "line")}


def b64(path):
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    with open(path, "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode()


def rich(text):
    if isinstance(text, (list, tuple)):
        text = " · ".join(map(str, text))
    t = html.escape(str(text))
    t = re.sub(r"&lt;(/?(?:strong|em|code))&gt;", r"<\1>", t).replace("&lt;br&gt;", "<br>")
    return re.sub(r"&lt;a href=&quot;(https?://[^&\s]*(?:&amp;[^&\s]*)*)&quot;&gt;(.*?)&lt;/a&gt;", r'<a href="\1" target="_blank" rel="noopener">\2</a>', t)


def check(spec, base):
    errs = check_retest(spec, base)
    if spec.get("retest") and not spec.get("rows"):
        return errs
    errs += [f"missing: {k}" for k in ("title", "lead", "columns", "rows") if not spec.get(k)]
    cols = spec.get("columns") or []
    red = False
    for i, r in enumerate(spec.get("rows") or [], 1):
        name = f"row {i} ({r.get('item', 'no item')})"
        cells = r.get("cells") or []
        if not r.get("item"):
            errs.append(f"{name}: item is missing")
        if len(cells) != len(cols):
            errs.append(f"{name}: {len(cells)} cells for {len(cols)} columns")
        bad = [c[0] for c in cells if c[0] not in CLS]
        if bad:
            errs.append(f"{name}: unknown cls {bad}, use {'/'.join(CLS)}")
        if any(c[0] in ("d", "x") for c in cells):
            red = True
            if not r.get("source"):
                errs.append(f"{name}: a d or x cell needs source; without one use o or n")
    figs = spec.get("figures") or []
    if red and not figs:
        errs.append("a row failed or differs but there is no figure to prove it")
    for i, f in enumerate(figs, 1):
        name = f"figure {i} ({f.get('title', 'no title')})"
        errs += [f"{name}: {k} is missing" for k in ("title", "why", "date") if not f.get(k)]
        if not f.get("image") and not f.get("evidence"):
            errs.append(f"{name}: needs image or evidence")
        if f.get("image") and not os.path.exists(os.path.join(base, f["image"])):
            errs.append(f"{name}: image not found: {f['image']}")
    for i, t in enumerate(spec.get("tickets") or [], 1):
        errs += [f"ticket {i}: {k} is missing" for k in ("id", "title") if not t.get(k)]
    if spec.get("rule"):
        errs += [f"rule: {k} is missing" for k in ("title", "items") if not spec["rule"].get(k)]
    if spec.get("table"):
        errs += [f"table: {k} is missing" for k in ("heading", "columns", "rows") if not spec["table"].get(k)]
    for s in spec.get("stats") or []:
        if "count" in s and s["count"] not in CLS:
            errs.append(f"stat {s.get('label')}: unknown count {s['count']}")
        elif "count" not in s and "value" not in s:
            errs.append(f"stat {s.get('label')}: needs value or count")
    return errs


BA_CSS = '''
.ba{background:#fff;font-family:-apple-system,"Inter","Helvetica Neue",Arial,sans-serif;color:#1f2328;padding:28px;border-radius:14px}
.ba h1{font-family:inherit;font-size:22px;line-height:1.3;font-weight:700;margin:0 0 4px;letter-spacing:0}
.ba .sub{color:#59636e;font-size:14px;margin-bottom:18px}
.ba .pass{display:inline-block;background:#dafbe1;color:#1a7f37;border:1px solid #aceebb;border-radius:999px;padding:2px 10px;font-size:13px;font-weight:600;margin-left:8px;vertical-align:3px}
.ba table{width:100%;min-width:0;border-collapse:separate;border-spacing:0;border:1px solid #d1d9e0;border-radius:10px;overflow:hidden;font-size:15px}
.ba thead th{position:static;background:#f6f8fa;text-align:left;font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:#59636e;font-weight:600;padding:10px 14px;border-bottom:1px solid #d1d9e0}
.ba tbody td{padding:14px;vertical-align:top;border-bottom:1px solid #eaeef2;line-height:1.4;background:none}
.ba tbody tr:last-child td{border-bottom:0}
.ba tbody tr:hover>*{background:none}
.ba td.check{width:210px;font-weight:600}
.ba td.before,.ba tbody tr:hover>td.before{width:40%;background:#fff8f7}
.ba td.after,.ba tbody tr:hover>td.after{background:#f6fef8}
.ba .lbl{font-size:12px;font-weight:700;margin-bottom:4px;text-transform:none;letter-spacing:0}
.ba .before .lbl{color:#cf222e}.ba .after .lbl{color:#1a7f37}
.ba img{display:block;max-width:100%;max-height:230px;margin-top:8px;border-radius:6px}
.ba .before img{border:2px solid #cf222e}.ba .after img{border:2px solid #1a7f37}
.ba .scroll{overflow-x:auto}.ba .scroll table{min-width:720px}
.ba .note{color:#59636e;font-size:13px;margin-top:12px}
'''
PNG_CSS = "*{box-sizing:border-box}body{margin:0;background:#fff}.ba{width:1100px;border-radius:0}"


def check_retest(spec, base):
    errs = []
    for i, t in enumerate(spec.get("retest") or [], 1):
        name = f"retest {i} ({t.get('id', 'no id')})"
        errs += [f"{name}: {k} is missing" for k in ("id", "title", "sub", "checks") if not t.get(k)]
        for j, c in enumerate(t.get("checks") or [], 1):
            errs += [f"{name} check {j}: {k} is missing" for k in ("check", "before", "after") if not c.get(k)]
            errs += [f"{name} check {j}: image not found: {c[k]}" for k in ("before_image", "after_image")
                     if c.get(k) and not os.path.exists(os.path.join(base, c[k]))]
    return errs


def before_after(t, base):
    def cell(side, label, c):
        img = c.get(f"{side}_image")
        img = f'<img src="{b64(os.path.join(base, img))}" alt="{label.title()}: {html.escape(c["check"])}">' if img else ""
        return f'<td class="{side}"><div class="lbl">{label}</div>{rich(c[side])}{img}</td>'
    trs = "".join(f'<tr><td class="check">{rich(c["check"])}</td>{cell("before", "BEFORE", c)}{cell("after", "AFTER ✓", c)}</tr>'
                  for c in t["checks"])
    note = f'<p class="note">Comment: {rich(t["comment"])}</p>' if t.get("comment") else ""
    return (f'<div class="ba" id="{html.escape(t["id"])}"><h1>{rich(t["id"])}: {rich(t["title"])}<span class="pass">QA passed</span></h1>'
            f'<div class="sub">{rich(t["sub"])}</div><div class="scroll"><table><thead><tr><th>Check</th><th>Before</th><th>After</th></tr></thead>'
            f'<tbody>{trs}</tbody></table></div>{note}</div>')


def chrome():
    found = [os.environ.get("CHROME", ""), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "/Applications/Chromium.app/Contents/MacOS/Chromium"]
    found += [shutil.which(n) or "" for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome")]
    return next((p for p in found if p and os.path.exists(p)), None)


def export_png(t, base, out_dir):
    """One light-theme PNG per ticket for a tracker comment; the HTML it was rendered from is kept beside it."""
    from PIL import Image, ImageChops
    exe = chrome()
    if not exe:
        sys.exit("--png needs Chrome or Chromium; set CHROME to its path")
    stem = os.path.join(out_dir, re.sub(r"[^\w.-]+", "-", t["id"]) + "-before-after")
    doc = (f'<!doctype html><meta charset="utf-8"><title>{html.escape(t["id"])}</title>'
           f'<style>{BA_CSS}{PNG_CSS}</style>{before_after({**t, "comment": ""}, base)}')
    with open(stem + ".html", "w", encoding="utf-8") as fh:
        fh.write(doc)
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--window-size=1160,3000", f"--screenshot={stem}.png", "file://" + os.path.abspath(stem + ".html")],
                   check=True, capture_output=True)
    im = Image.open(stem + ".png").convert("RGB")
    box = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if box:
        im = im.crop((0, 0, im.width, min(im.height, box[3] + 56)))
    im.save(stem + ".png")
    return stem + ".png"


def stat(s, rows):
    if "count" in s:
        worst = [next(k for k in WORST if k in {c[0] for c in r["cells"]}) for r in rows]
        value = f"{worst.count(s['count'])} / {len(worst)}"
    else:
        value = str(s["value"])
    m = re.match(r"\s*(\d+)\s*(?:/|of)\s*(\d+)", value)
    bar = ""
    if m and int(m.group(2)):
        pct = min(100, round(100 * int(m.group(1)) / int(m.group(2))))
        good = s.get("count", "ok") == "ok" and pct == 100
        bar = f'<div class="bar"><i{"" if good else " class=" + chr(34) + "part" + chr(34)} style="width:{pct}%"></i></div>'
    return f'<div class="card stat"><span class="muted">{rich(s.get("label", ""))}</span><b>{rich(value)}</b>{bar}<span class="muted">{rich(s.get("note", ""))}</span></div>'


def figure(n, f, cols, base):
    e = html.escape
    tested = f.get("tested") or f.get("contests") or []
    chips = "".join(f'<span class="chip">{rich(c)}</span>' for c in tested)
    chips = f'<div class="chips"><span class="lbl">Tested on</span>{chips}</div>' if chips else ""
    steps = "<ol>" + "".join(f"<li>{rich(x)}</li>" for x in f["steps"]) + "</ol>" if f.get("steps") else ""
    facts = [("Severity", rich(f.get("severity", ""))), ("Steps", steps), ("Expected", rich(f.get("expected", ""))),
             ("Actual", rich(f.get("actual", ""))), ("Captured", rich(f["date"]))]
    dl = "<dl>" + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts if v) + "</dl>"
    tk = f'<p class="tk">Tickets: {rich(f["tickets"])}</p>' if f.get("tickets") else ""
    media = ""
    if f.get("image"):
        media += (f'<button class="zoom" type="button" aria-label="Enlarge image: {e(f["title"])}"><img loading="lazy" '
                  f'src="{b64(os.path.join(base, f["image"]))}" alt="{e(" vs ".join(cols))}: {e(f["title"])}"></button>')
    if f.get("evidence"):
        ev = f["evidence"]
        media += f'<pre>{e(chr(10).join(map(str, ev)) if isinstance(ev, list) else str(ev))}</pre>'
    return (f'<figure class="card fig" id="fig{n}"><figcaption><span class="num">{n}</span><div><h3>{rich(f["title"])}</h3>'
            f'<p class="muted">{rich(f.get("subtitle", ""))}</p>{chips}<p class="why">{rich(f["why"])}</p>{dl}{tk}</div></figcaption>{media}</figure>')


def ticket(t):
    url = t.get("url", "")
    link = bool(re.match(r"https?://", url))
    tag = f'a class="card tkt" href="{html.escape(url)}" target="_blank" rel="noopener"' if link else 'div class="card tkt"'
    return (f'<{tag}><span class="id">{rich(t["id"])}</span><h3>{rich(t["title"])}</h3>'
            f'<span class="cnt">{rich(t.get("note", ""))}</span></{"a" if link else "div"}>')


def build(spec, base):
    cols, rows, retest = spec.get("columns") or [], spec.get("rows") or [], spec.get("retest") or []
    if retest and not rows:  # fix-retest only: a verdict line is all the header needs
        spec.setdefault("title", "Fix retest: " + ", ".join(t["id"] for t in retest))
        spec.setdefault("lead", f"<strong>{len(retest)} fix{'es' if len(retest) > 1 else ''} retested.</strong> "
                        + " · ".join(f'{t["id"]}: QA passed' for t in retest))
    h = {"tickets": "Tickets", "rows": "Results", "retest": "Before / after", "figures": "Proof", "open": "Open items",
         **(spec.get("headings") or {})}
    parts, nav = [], [("summary", "Summary")]

    def add(anchor, title, inner):
        nav.append((anchor, title))
        parts.append(f'<section id="{anchor}"><h2>{rich(title)}</h2>{inner}</section>')

    stats = "".join(stat(s, rows) for s in spec.get("stats") or [])
    rule = spec.get("rule")
    rule_html = (f'<div class="card rule"><h3>{rich(rule["title"])}</h3><ul>' + "".join(f"<li>{rich(x)}</li>" for x in rule["items"]) + "</ul></div>") if rule else ""
    if spec.get("tickets"):
        add("tickets", h["tickets"], '<div class="grid3">' + "".join(ticket(t) for t in spec["tickets"]) + "</div>")
    used = {c[0] for r in rows for c in r["cells"]}
    names = {**CLS, **(spec.get("legend") or {})}
    legend = "".join(f'<span><i class="sw" style="background:var(--{SW[k][0]});outline:1px solid var(--{SW[k][1]})"></i>{rich(v)}</span>' for k, v in names.items() if k in used)
    narrow = ' style="min-width:0"' if len(cols) < 3 else ""
    has_tk = any(r.get("ticket") for r in rows)
    head = "".join(f"<th>{rich(c)}</th>" for c in cols) + ("<th>Ticket</th>" if has_tk else "")
    trs = "".join(
        f'<tr><th scope="row">{rich(r["item"])}' + (f'<span class="src">Source: {rich(r["source"])}</span>' if r.get("source") else "") + "</th>"
        + "".join(f'<td class="{c[0]}">{rich(c[1])}</td>' for c in r["cells"])
        + (f'<td class="tk">{rich(r.get("ticket", ""))}</td>' if has_tk else "") + "</tr>" for r in rows)
    if rows:
        add("results", h["rows"], f'<div class="legend">{legend}</div><div class="tbl"><table{narrow}><thead><tr><th>Item</th>{head}</tr></thead><tbody>{trs}</tbody></table></div>')
    if retest:
        add("retest", h["retest"], '<div class="figs">' + "".join(f'<div class="card">{before_after(t, base)}</div>' for t in retest) + "</div>")
    if spec.get("figures"):
        add("proof", h["figures"], '<p class="muted">Click an image to enlarge it.</p><div class="figs">'
            + "".join(figure(n, f, cols, base) for n, f in enumerate(spec["figures"], 1)) + "</div>")
    tb = spec.get("table")
    if tb:
        th = "".join(f"<th>{rich(c)}</th>" for c in tb["columns"])
        body = "".join("<tr>" + "".join(f"<td>{rich(x)}</td>" for x in r) + "</tr>" for r in tb["rows"])
        add("tested", tb["heading"], f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>')
    if spec.get("open"):
        add("open", h["open"], '<div class="card notes"><ul>' + "".join(f"<li>{rich(x)}</li>" for x in spec["open"]) + "</ul></div>")
    navh = "".join(f'<a href="#{a}">{rich(t)}</a>' for a, t in nav)
    return f'''<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(spec["title"])}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600&display=swap">
<style>body{{margin:0}}{CSS}{BA_CSS if retest else ""}</style>
<nav class="nav" aria-label="Sections"><div class="nav-in">{navh}</div></nav>
<div class="wrap">
<header class="hero" id="summary"><div><p class="eyebrow">{rich(spec.get("eyebrow", ""))}</p><h1>{rich(spec["title"])}</h1></div>
<p class="lead">{rich(spec["lead"])}</p><div class="stats">{stats}</div>{rule_html}</header>
{"".join(parts)}
</div>
<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Enlarged image"><img alt=""></div>
<script>
(function(){{var lb=document.getElementById('lb'),im=lb.querySelector('img');
document.querySelectorAll('.zoom').forEach(function(b){{b.addEventListener('click',function(){{im.src=b.querySelector('img').src;lb.classList.add('on');}});}});
lb.addEventListener('click',function(){{lb.classList.remove('on');}});
document.addEventListener('keydown',function(e){{if(e.key==='Escape')lb.classList.remove('on');}});}})();
</script>'''


def main():
    png = "--png" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--png"]
    if len(args) != 2 or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if "-h" in sys.argv or "--help" in sys.argv else 2)
    sys.argv[1:] = args
    with open(sys.argv[1], encoding="utf-8") as fh:
        spec = json.load(fh)
    spec.setdefault("columns", spec.get("platforms"))
    base = os.path.dirname(os.path.abspath(sys.argv[1]))
    errs = check(spec, base)
    if errs:
        sys.exit("spec not complete, no page written:\n  - " + "\n  - ".join(errs))
    with open(sys.argv[2], "w", encoding="utf-8") as fh:
        fh.write(build(spec, base))
    print("wrote", sys.argv[2])
    if png:
        if not spec.get("retest"):
            sys.exit("--png exports retest tickets; this spec has none")
        for t in spec["retest"]:
            print("wrote", export_png(t, base, os.path.dirname(os.path.abspath(sys.argv[2]))), "| comment:", t.get("comment", ""))


if __name__ == "__main__":
    main()
