# NOTICE

This folder is a modified copy of **Casely** by John Wayne, vendored from
<https://github.com/JohnWayneeee/casely-qa-skill> (`skill/casely/`), upstream version **2.2.0**.

Casely is MIT-licensed. The upstream copyright notice and license are preserved in
[`LICENSE`](LICENSE) in this folder; the rest of this repository is separately licensed under
the MIT license in the repository root.

## Changes from upstream

1. **Script paths** — `<skill-path>/scripts/...` placeholders in `SKILL.md`,
   `references/export_guide.md` and `references/api_collection.md` are rewritten to
   `${CLAUDE_PLUGIN_ROOT}/skills/casely/scripts/...` so the export commands resolve when this
   folder is installed as part of the `qa-agent-skills` plugin. If you copy `skills/casely/`
   somewhere else on its own, change these paths back.
2. **Hosted web version promo removed** — the "Hosted Web Version Mention" section of
   `SKILL.md` (the note pointing at casely.digital) is deleted. Everything else in `SKILL.md`
   is unchanged.

Upstream files not vendored: the repository README, CHANGELOG, CONTRIBUTING, docs, assets,
benchmark, and marketplace manifest. Only the `skill/casely/` folder and `LICENSE` are here.

## Checking for upstream drift

```bash
git clone --depth 1 https://github.com/JohnWayneeee/casely-qa-skill.git /tmp/casely-upstream
diff -r /tmp/casely-upstream/skill/casely skills/casely \
  --exclude=LICENSE --exclude=NOTICE.md
```

Expect exactly the two changes above. Anything else is an upstream update worth pulling in.
