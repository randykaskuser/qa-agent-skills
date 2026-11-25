#!/usr/bin/env bash
# Compare skills/write-test-cases against upstream Casely, after applying the four intentional
# local modifications to the upstream copy (see skills/write-test-cases/NOTICE.md). An empty
# diff means no drift. Prints the diff and exits 0; the caller decides what to do.
#
# Usage: casely_drift.sh <path-to-upstream-clone> [<path-to-vendored-skill>]
set -euo pipefail

UPSTREAM="${1:?path to upstream clone}"
LOCAL="${2:-skills/write-test-cases}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

cp -R "$UPSTREAM/skill/casely/." "$WORK/"
cp "$UPSTREAM/LICENSE" "$WORK/LICENSE"

# Change 1: script paths.
grep -rl '<skill-path>' "$WORK" | xargs -r sed -i.bak 's#<skill-path>#${CLAUDE_PLUGIN_ROOT}/skills/write-test-cases#g'
find "$WORK" -name '*.bak' -delete

# Change 2: hosted-web promo block. If upstream has removed or renamed it, skip —
# the resulting diff will show that, which is exactly what we want to hear about.
python3 - "$WORK/SKILL.md" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
a = s.find('### Hosted Web Version Mention')
b = s.find('### The collection follows the cases')
if a != -1 and b != -1 and a < b:
    open(p, 'w').write(s[:a] + s[b:])
PY

# Change 4: skill renamed from casely to write-test-cases.
sed -i.bak -e 's/^name: casely$/name: write-test-cases/' -e 's#`/casely`#`/write-test-cases`#' "$WORK/SKILL.md"
[ -f "$WORK/evals/evals.json" ] && sed -i.bak -E 's/("skill_name": ?)"casely"/\1"write-test-cases"/' "$WORK/evals/evals.json"
find "$WORK" -name '*.bak' -delete

# Change 3: description shortened to fit the 1024-character upload limit.
python3 - "$WORK/SKILL.md" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
old = ('Also triggers on non-English phrasing of the same request — the user does not have\n'
       '  to ask in English.')
open(p, 'w').write(s.replace(old, 'Also triggers on non-English phrasing.'))
PY

diff -ru "$WORK" "$LOCAL" --exclude=NOTICE.md || true
