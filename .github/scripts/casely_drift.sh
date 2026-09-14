#!/usr/bin/env bash
# Compare skills/casely against upstream Casely, after applying the two intentional
# local modifications to the upstream copy (see skills/casely/NOTICE.md). An empty
# diff means no drift. Prints the diff and exits 0; the caller decides what to do.
#
# Usage: casely_drift.sh <path-to-upstream-clone> [<path-to-vendored-skill>]
set -euo pipefail

UPSTREAM="${1:?path to upstream clone}"
LOCAL="${2:-skills/casely}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

cp -R "$UPSTREAM/skill/casely/." "$WORK/"
cp "$UPSTREAM/LICENSE" "$WORK/LICENSE"

# Change 1: script paths.
grep -rl '<skill-path>' "$WORK" | xargs -r sed -i.bak 's#<skill-path>#${CLAUDE_PLUGIN_ROOT}/skills/casely#g'
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

diff -ru "$WORK" "$LOCAL" --exclude=NOTICE.md || true
