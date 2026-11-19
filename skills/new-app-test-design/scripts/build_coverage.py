#!/usr/bin/env python3
"""Build the coverage page (one row per feature, its tickets, its case chips) from the case catalogue.

  build_coverage.py --catalogue docs/test-cases/web-player.yml --prefix WEB- \
      --rows rows.json --config config.json [--statuses statuses.json] --out coverage.html

rows.json: a list, or {"rows": [...]}. One row per feature (or per ticket):
  {"group": "Player", "area": "Sticky mini player",
   "tickets": [["WEB-502", "In Review"], ["WEB-504", "Todo"]],   # any number, any teams
   "cases": ["WEB-0125", "WEB-0126"],                            # ids, or bare numbers (prefix added)
   "note": "No staging content yet"}                            # optional
  A ticket may be a bare id ("WEB-502"); its status then comes from --statuses {"WEB-502": "In Review"}.
  Legacy rows with "ios" / "andr" ([id, status] or null) are accepted and turned into "tickets".

config.json:
  {"title": "Player v2 coverage", "brand": "Acme QA", "updated": "19 Nov 2026",
   "subtitle": "Test cases per ticket ...", "id_prefix": "WEB-",
   "ticket_url": "https://linear.app/acme/issue/{id}", "case_url": "https://qa.example/cases?case={id}",
   "teams": ["IOS", "AND"], "team_labels": {"IOS": "iOS", "AND": "Android"},
   "done_status": "In Review",
   "nav": [{"label": "Test plan", "url": "https://..."}],
   "banners": [{"label": "Release rule", "text": "Every P0 case must pass."},
               {"label": "Blocked", "kind": "warn", "text": "2 conflicts wait for a ruling:", "url": "https://...", "link_text": "QUA-200"}]}
  Only "title" and "updated" are required. teams defaults to the ticket prefixes in row order.

Fails (exit 1) when a row names a case that is not in the catalogue or a ticket with no status.
Warns about catalogue cases in --ids that no row lists, and rows with no cases.
"""
import argparse, json, os, sys

try:
    import yaml
except ImportError:
    sys.exit('build_coverage.py needs PyYAML: pip install pyyaml')

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--catalogue', required=True)
    ap.add_argument('--prefix', required=True, help='case id prefix, e.g. MOB- or WEB-')
    ap.add_argument('--rows', required=True)
    ap.add_argument('--config', required=True)
    ap.add_argument('--statuses', help='JSON {ticket id: status} for rows that give bare ticket ids')
    ap.add_argument('--ids', help='case range the page should cover, e.g. MOB-0072..MOB-0282 (warns on cases no row lists)')
    ap.add_argument('--template', default=os.path.join(HERE, '..', 'assets', 'coverage.tpl.html'))
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    cat = {c['id']: c for c in yaml.safe_load(open(a.catalogue, encoding='utf-8')) or []}
    raw = json.load(open(a.rows, encoding='utf-8'))
    rows_in = raw['rows'] if isinstance(raw, dict) else raw
    cfg = json.load(open(a.config, encoding='utf-8'))
    cfg.setdefault('id_prefix', a.prefix)
    statuses = json.load(open(a.statuses, encoding='utf-8')) if a.statuses else {}
    for k in ('title', 'updated'):
        if not cfg.get(k): sys.exit(f'config.json needs "{k}"')

    errors, warns, rows, used = [], [], [], set()
    for i, r in enumerate(rows_in):
        tickets = r.get('tickets')
        if tickets is None:
            tickets = [t for t in (r.get('ios'), r.get('andr')) if t]
        fixed = []
        for t in tickets:
            tid, st = (t, None) if isinstance(t, str) else (t[0], t[1] if len(t) > 1 else None)
            st = st or statuses.get(tid)
            if not st: errors.append(f'row {i} ({r.get("area")}): ticket {tid} has no status')
            fixed.append([tid, st or 'Unknown'])
        cases = []
        for c in r.get('cases', []):
            cid = f'{a.prefix}{int(c):04d}' if isinstance(c, int) or str(c).isdigit() else str(c)
            if cid not in cat: errors.append(f'row {i} ({r.get("area")}): case {cid} is not in {a.catalogue}')
            cases.append(cid); used.add(cid)
        if not cases: warns.append(f'row {i} ({r.get("area")}): no cases')
        rows.append({'group': r.get('group'), 'area': r['area'], 'tickets': fixed, 'cases': cases, 'note': r.get('note')})

    if a.ids:
        lo, hi = (int(x[len(a.prefix):]) for x in a.ids.split('..'))
        orphans = [c for c in cat if c.startswith(a.prefix) and lo <= int(c[len(a.prefix):]) <= hi and c not in used]
        if orphans: warns.append(f'{len(orphans)} cases in {a.ids} are in no row: {", ".join(orphans)}')

    data = {'config': cfg, 'rows': rows,
            'cases': {c: {k: cat[c].get(k) for k in ('title', 'priority', 'scope', 'kind')} for c in sorted(used) if c in cat}}
    tpl = open(a.template, encoding='utf-8').read()
    if '__DATA__' not in tpl: sys.exit(f'{a.template} has no __DATA__ placeholder')
    js = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    html = tpl.replace('__TITLE__', cfg['title'].replace('<', '&lt;')).replace('__DATA__', js)
    for w in warns: print('WARN:', w)
    for e in errors: print('ERROR:', e)
    if errors: sys.exit(1)
    open(a.out, 'w', encoding='utf-8').write(html)
    print(f'OK: {len(rows)} rows, {len(used)} cases, {sum(len(r["tickets"]) for r in rows)} tickets -> {a.out}')


if __name__ == '__main__':
    main()
