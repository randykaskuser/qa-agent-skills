"""Build the consistency-check proof page (one self-contained HTML file, light theme only).

Usage: python3 build_artifact.py spec.json out.html
Images in the spec are paths relative to spec.json (jpg or png); they are embedded as base64.
Spec keys: title, eyebrow, lead, platforms[], stats[{label,value,note}], rule{title,items[]},
tickets[{id,title,note,url}], rows[{item,cells[[cls,text]...],ticket}] (cls: ok | d | n),
figures[{image,title,subtitle,contests[],why,tickets}],
table{heading,columns[],rows[[...]]} (optional, e.g. the contests tested), open[html strings].
cls: ok = matches the source of truth, d = differs, n = observed, no source.
"""
import base64, html, json, mimetypes, os, sys

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
.stat{padding:16px;display:grid;gap:8px}
.stat b{font-family:var(--display);font-size:26px;font-weight:600}
.bar{height:8px;border-radius:99px;background:var(--line);overflow:hidden}.bar i{display:block;height:100%;background:var(--ok);border-radius:99px}
.rule{padding:16px 18px;display:grid;gap:6px;border-left:4px solid var(--accent)}
.rule ul{margin:0;padding-left:18px;display:grid;gap:4px}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.tkt{padding:16px;display:grid;gap:6px;text-decoration:none;color:inherit}
.tkt:hover{border-color:var(--accent)}
.tkt .id{font-family:var(--display);font-weight:600;color:var(--accent)}
.tkt .cnt{font-size:13px;color:var(--muted)}
.tbl{border:1px solid var(--line);border-radius:14px;background:var(--surface);box-shadow:var(--shadow)}
@media (max-width:900px){.tbl{overflow-x:auto;-webkit-overflow-scrolling:touch}}
table{width:100%;border-collapse:separate;border-spacing:0;font-size:14px;min-width:760px}
th,td{text-align:left;padding:11px 14px;border-bottom:1px solid var(--line);vertical-align:top}
thead th{position:sticky;top:calc(env(safe-area-inset-top,0px) + 53px);z-index:5;background:var(--surface2);font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:600;white-space:nowrap}
tbody th{font-weight:600;background:var(--surface);min-width:150px}
tbody tr:last-child>*{border-bottom:0}
tbody tr:hover>*{background:var(--surface2)}
td.ok{background:var(--ok-bg)}td.d{background:var(--bad-bg)}td.n{background:transparent}
td.ok::before,td.d::before{display:inline-block;margin-right:6px;font-weight:700}
td.ok::before{content:"✓";color:var(--ok)}td.d::before{content:"≠";color:var(--bad)}
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
@media (max-width:640px){h1{font-size:27px}.fig{padding:14px}}
'''

def b64(path):
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()

def build(spec, base):
    e = html.escape
    plats = spec["platforms"]
    stats = "".join(
        f'<div class="card stat"><span class="muted">{e(s["label"])}</span><b>{e(s["value"])}</b>'
        f'<div class="bar"><i style="width:100%"></i></div><span class="muted">{e(s.get("note", ""))}</span></div>'
        for s in spec.get("stats", []))
    rule = spec.get("rule")
    rule_html = (f'<div class="card rule"><h3>{e(rule["title"])}</h3><ul>' + "".join(f"<li>{e(x)}</li>" for x in rule["items"]) + "</ul></div>") if rule else ""
    tickets = "".join(
        f'<a class="card tkt" href="{e(t["url"])}" target="_blank" rel="noopener"><span class="id">{e(t["id"])}</span>'
        f'<h3>{e(t["title"])}</h3><span class="cnt">{e(t.get("note", ""))}</span></a>' for t in spec.get("tickets", []))
    head = "".join(f"<th>{e(p)}</th>" for p in plats)
    rows = "".join(
        f'<tr><th scope="row">{e(r["item"])}</th>' + "".join(f'<td class="{c[0]}">{e(c[1])}</td>' for c in r["cells"]) +
        f'<td class="tk">{e(r.get("ticket", ""))}</td></tr>' for r in spec.get("rows", []))
    figs = ""
    for n, f in enumerate(spec.get("figures", []), 1):
        chips = "".join(f'<span class="chip">{e(c)}</span>' for c in f.get("contests", []))
        figs += (f'<figure class="card fig" id="fig{n}"><figcaption><span class="num">{n}</span><div><h3>{e(f["title"])}</h3>'
                 f'<p class="muted">{e(f.get("subtitle", ""))}</p><div class="chips"><span class="lbl">Tested on</span>{chips}</div>'
                 f'<p class="why">{e(f["why"])}</p><p class="tk">Tickets: {e(f.get("tickets", ""))}</p></div></figcaption>'
                 f'<button class="zoom" type="button" aria-label="Enlarge image: {e(f["title"])}"><img loading="lazy" '
                 f'src="{b64(os.path.join(base, f["image"]))}" alt="{e(" vs ".join(plats))}: {e(f["title"])}"></button></figure>')
    tb = spec.get("table")
    table_html = ""
    if tb:
        th = "".join(f"<th>{e(c)}</th>" for c in tb["columns"])
        trs = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in tb["rows"])
        table_html = f'<section id="table"><h2>{e(tb["heading"])}</h2><div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div></section>'
    openl = "".join(f"<li>{x}</li>" for x in spec.get("open", []))
    nav = ["Summary", "Tickets", "Differences", "Proof"] + ([tb["heading"]] if tb else []) + ["Open items"]
    anchors = ["summary", "tickets", "differences", "proof"] + (["table"] if tb else []) + ["open"]
    navh = "".join(f'<a href="#{a}">{e(t)}</a>' for a, t in zip(anchors, nav))
    return f'''<title>{e(spec["title"])}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600&display=swap">
<style>{CSS}</style>
<nav class="nav" aria-label="Sections"><div class="nav-in">{navh}</div></nav>
<div class="wrap">
<header class="hero" id="summary"><div><p class="eyebrow">{e(spec.get("eyebrow", ""))}</p><h1>{e(spec["title"])}</h1></div>
<p class="lead">{spec.get("lead", "")}</p><div class="stats">{stats}</div>{rule_html}</header>
<section id="tickets"><h2>Parent tickets</h2><div class="grid3">{tickets}</div></section>
<section id="differences"><h2>Differences between platforms</h2>
<div class="legend"><span><i class="sw" style="background:var(--bad-bg);outline:1px solid var(--bad)"></i>differs from the source of truth or the others</span><span><i class="sw" style="background:var(--ok-bg);outline:1px solid var(--ok)"></i>matches</span><span><i class="sw" style="background:var(--surface);outline:1px solid var(--line)"></i>observed, no source</span></div>
<div class="tbl"><table><thead><tr><th>Item</th>{head}<th>Ticket</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section id="proof"><h2>Proof</h2><p class="muted">Same step, same state on every platform. Red differs, green matches, amber is a different pattern with no source. Click an image to enlarge.</p><div class="figs">{figs}</div></section>
{table_html}
<section id="open"><h2>Open items</h2><div class="card notes"><ul>{openl}</ul></div></section>
</div>
<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Enlarged image"><img alt=""></div>
<script>
(function(){{var lb=document.getElementById('lb'),im=lb.querySelector('img');
document.querySelectorAll('.zoom').forEach(function(b){{b.addEventListener('click',function(){{im.src=b.querySelector('img').src;lb.classList.add('on');}});}});
lb.addEventListener('click',function(){{lb.classList.remove('on');}});
document.addEventListener('keydown',function(e){{if(e.key==='Escape')lb.classList.remove('on');}});}})();
</script>'''

if __name__ == "__main__":
    spec_path, out = sys.argv[1], sys.argv[2]
    open(out, "w").write(build(json.load(open(spec_path)), os.path.dirname(os.path.abspath(spec_path))))
    print("wrote", out)
