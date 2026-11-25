#!/usr/bin/env python3
"""Apply reviewer patches to a YAML case catalogue, or check it against the case rules.

Unchanged cases stay byte for byte; edited and new cases are re-emitted in the
catalogue's own key order. New cases get the next free ids.

  apply_patches.py <catalogue.yml> --prefix MOB- patch-A.json [patch-B.json ...] [--newmap new.json]
  apply_patches.py <catalogue.yml> --prefix MOB- --check [--ids MOB-0072..MOB-0282]

Patch JSON (one file per reviewer):
  {"edits": [{"id": "MOB-0133", "set": {"expected": "1. ...\n2. ..."}}],
   "new":   [{"sibling": "MOB-0072", "row": 3, "covers": "IOS-12 AC2",
              "title": "...", "priority": "P1", "steps": "1. ...", "expected": "1. ...",
              "description": "...", "preconditions": "...", "tags": [...]}]}

A new case copies every field from its sibling, then takes the fields it gives.
Rules enforced on every edited or new case (and on all cases with --check):
  - steps and expected have the same number of lines
  - priority P0/P1 -> scope regression, type tag smoke|regression; P2/P3 -> scope extended,
    type tag extended, automation manual (a scope that differs from the priority needs a reason)
  - automation not-automatable needs a reason
Exit code 1 when a problem is found. Needs PyYAML.
"""
import argparse, json, re, sys

try:
    import yaml
except ImportError:
    sys.exit('apply_patches.py needs PyYAML: pip install pyyaml')

TYPE_TAGS = ('smoke', 'regression', 'extended')
NEVER_SET = {'id'}


def scalar(v):
    if v is None: return 'null'
    if isinstance(v, bool): return 'true' if v else 'false'
    if isinstance(v, int): return str(v)
    if isinstance(v, list): return '[' + ', '.join(scalar(x) for x in v) + ']'
    s = str(v)
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ,.'()/&+·–—-]*[A-Za-z0-9.)']", s) and ': ' not in s and ' #' not in s:
        return s
    return json.dumps(s, ensure_ascii=False)


def lines(v):
    return [l.strip() for l in str(v or '').strip().split('\n') if l.strip()]


def emit(c, keys):
    out = []
    for k in keys + [k for k in c if k not in keys]:
        if k not in c: continue
        v = c[k]
        if k in ('steps', 'expected'):
            out.append(f'  {k}: |-')
            out += ['    ' + l for l in lines(v)]
        elif k in ('description', 'preconditions'):
            out.append(f'  {k}: {json.dumps(v, ensure_ascii=False) if v is not None else "null"}')
        else:
            out.append(f'  {k}: {scalar(v)}')
    out[0] = '- ' + out[0][2:]
    return '\n'.join(out) + '\n'


def fix_scope(c):
    """Make scope, type tag and automation follow priority."""
    if 'priority' not in c: return
    reg = c['priority'] in ('P0', 'P1')
    if 'scope' in c: c['scope'] = 'regression' if reg else 'extended'
    if isinstance(c.get('tags'), list):
        had_smoke = 'smoke' in c['tags']
        tags = [t for t in c['tags'] if t not in TYPE_TAGS]
        tags.append(('smoke' if had_smoke else 'regression') if reg else 'extended')
        c['tags'] = tags
    if 'automation' in c:
        if not reg: c['automation'] = 'manual'
        elif c['automation'] == 'manual': c['automation'] = 'automatable'


def problems_of(c):
    p, cid = [], c.get('id', '?')
    if len(lines(c.get('steps'))) != len(lines(c.get('expected'))):
        p.append(f'{cid}: {len(lines(c.get("steps")))} steps vs {len(lines(c.get("expected")))} expected lines')
    pr = c.get('priority')
    if pr in ('P0', 'P1', 'P2', 'P3'):
        reg = pr in ('P0', 'P1')
        if 'scope' in c and c['scope'] != ('regression' if reg else 'extended') and not c.get('reason'):
            p.append(f'{cid}: {pr} with scope {c["scope"]} and no reason')
        tt = [t for t in (c.get('tags') or []) if t in TYPE_TAGS]
        if isinstance(c.get('tags'), list) and (len(tt) != 1 or (tt[0] == 'extended') == reg):
            p.append(f'{cid}: {pr} with type tags {tt or "none"}')
        if not reg and c.get('automation') not in (None, 'manual'):
            p.append(f'{cid}: {pr} with automation {c["automation"]}')
    if c.get('automation') == 'not-automatable' and not c.get('reason'):
        p.append(f'{cid}: not-automatable without a reason')
    return p


def in_range(cid, rng, prefix):
    if not rng: return True
    a, b = rng.split('..')
    n = lambda x: int(x[len(prefix):])
    return n(a) <= n(cid) <= n(b)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('catalogue')
    ap.add_argument('patches', nargs='*')
    ap.add_argument('--prefix', required=True, help='case id prefix, e.g. MOB- or WEB-')
    ap.add_argument('--check', action='store_true', help='only report rule problems, write nothing')
    ap.add_argument('--ids', help='with --check: limit to a range, e.g. MOB-0072..MOB-0282')
    ap.add_argument('--newmap', help='write the new ids (id, row, title, priority, covers) to this JSON file')
    ap.add_argument('--reset', default='reason', help='comma list of fields a new case does not copy from its sibling (set to null, [] for lists)')
    ap.add_argument('--dry-run', action='store_true', help='apply in memory, print the report, write nothing')
    a = ap.parse_intermixed_args()

    text = open(a.catalogue, encoding='utf-8').read()
    m = re.search(r'^- id: ', text, re.M)
    if not m: sys.exit(f'{a.catalogue}: no "- id:" entries found')
    head, body = text[:m.start()], text[m.start():]
    blocks = [b for b in re.split(r'(?m)^(?=- id: )', body) if b]
    cases, order, keys = {}, [], []
    for b in blocks:
        d = yaml.safe_load(b)[0]
        for k in d:
            if k not in keys: keys.append(k)
        cases[d['id']] = {'raw': b, 'd': d, 'dirty': False}
        order.append(d['id'])

    if a.check:
        probs = [x for cid in order if in_range(cid, a.ids, a.prefix) for x in problems_of(cases[cid]['d'])]
        print(f'CHECKED: {sum(in_range(c, a.ids, a.prefix) for c in order)} cases')
        print('PROBLEMS:', len(probs)); [print(' ', x) for x in probs]
        sys.exit(1 if probs else 0)

    problems, log, news = [], [], []
    reset = [k for k in a.reset.split(',') if k]
    for p in a.patches:
        P = json.load(open(p, encoding='utf-8'))
        for e in P.get('edits', []):
            cid = e.get('id')
            if cid not in cases:
                problems.append(f'{p}: unknown id {cid}'); continue
            c = cases[cid]['d']
            for k, v in e.get('set', {}).items():
                if k in NEVER_SET: problems.append(f'{p}: {cid} tries to set {k}'); continue
                c[k] = v
            fix_scope(c)
            cases[cid]['dirty'] = True
            log.append(f'edit {cid}: {", ".join(e.get("set", {}))}')
        for n in P.get('new', []):
            sib = cases.get(n.get('sibling'))
            if not sib:
                problems.append(f'{p}: new "{n.get("title")}" has unknown sibling {n.get("sibling")}'); continue
            c = json.loads(json.dumps(sib['d'], default=str))
            for k in reset:
                if k in c: c[k] = [] if isinstance(c[k], list) else None
            for k, v in n.items():
                if k in ('sibling', 'row', 'covers') or k in NEVER_SET: continue
                c[k] = v
            fix_scope(c)
            news.append((n.get('row'), c, n.get('covers', '')))

    nums = [int(i[len(a.prefix):]) for i in order if i.startswith(a.prefix) and i[len(a.prefix):].isdigit()]
    last, width = max(nums or [0]), max([len(i) - len(a.prefix) for i in order if i.startswith(a.prefix)] or [4])
    newmap = []
    for row, c, cov in sorted(news, key=lambda x: (x[0] if x[0] is not None else 10**9)):
        last += 1
        c['id'] = f'{a.prefix}{last:0{width}d}'
        newmap.append({'id': c['id'], 'row': row, 'title': c.get('title'), 'priority': c.get('priority'), 'covers': cov})
        cases[c['id']] = {'raw': None, 'd': c, 'dirty': True}
        order.append(c['id'])

    for cid in order:
        if cases[cid]['dirty']: problems += problems_of(cases[cid]['d'])

    out = head + ''.join(emit(cases[i]['d'], keys) if cases[i]['dirty'] else cases[i]['raw'] for i in order)
    if not out.endswith('\n'): out += '\n'
    if not a.dry_run:
        open(a.catalogue, 'w', encoding='utf-8').write(out)
        if a.newmap: json.dump(newmap, open(a.newmap, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('\n'.join(log))
    print('NEW:', len(newmap)); [print(' ', x['id'], 'row', x['row'], x['priority'], x['title']) for x in newmap]
    print('PROBLEMS:', len(problems)); [print(' ', x) for x in problems]
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
