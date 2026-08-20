# last30days local customizations

Backup of the only three things in `~/.claude/skills/last30days` that are **not**
upstream. Everything else in that directory is a plain clone of
`mvanhorn/last30days-skill` and needs no backup.

These files were untracked by git in their original location, so this directory is
their only version history.

| File here | Restores to |
|---|---|
| `gdrive.py` | `~/.claude/skills/last30days/scripts/lib/gdrive.py` |
| `setup_gdrive.py` | `~/.claude/skills/last30days/setup_gdrive.py` |
| `SKILL.md.local-section.md` | a section inside `~/.claude/skills/last30days/SKILL.md` |

## Re-applying after an upstream merge

Per the root `CLAUDE.md`, the skill clone loads the **flat copy at the repo root**
(`SKILL.md` + `scripts/` + `agents/` + `assets/` + `references/`), which is an
untracked mirror of `skills/last30days/*`. Merging upstream overwrites that mirror,
which drops all three customizations. Restore them like this:

```bash
cd ~/.claude/skills/last30days
git fetch upstream --tags
git merge --ff-only upstream/main

# refresh the flat root mirror
cp skills/last30days/SKILL.md .
cp -r skills/last30days/{scripts,agents,assets,references} .

# re-apply customization 1 and 2
cp /path/to/this/repo/skill-customizations/gdrive.py scripts/lib/gdrive.py
cp /path/to/this/repo/skill-customizations/setup_gdrive.py .
```

For customization 3, paste the contents of `SKILL.md.local-section.md` into
`SKILL.md` **immediately before** the `## WAIT FOR USER'S RESPONSE` header. That
placement is load-bearing: the section must run after synthesis is displayed and
after any HTML brief flow.

Verify with:

```bash
grep -c "LOCAL TEXT REPORT" ~/.claude/skills/last30days/SKILL.md   # expect 1
ls ~/.claude/skills/last30days/scripts/lib/gdrive.py
```

## Credentials

None are stored here. Both scripts read from `~/.config/last30days/`:

- `gdrive_credentials.json` - OAuth client, downloaded from Google Cloud Console
- `gdrive_token.json` - cached access token, minted by the consent flow

Those two files are **not** in this repo and must never be committed. The root
`.gitignore` blocks both by name. To rebuild them on a new machine:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
python ~/.claude/skills/last30days/setup_gdrive.py
```

## Call contract

`upload_report(path, topic)` takes a `Path`, not a `str`, and `topic` is a logging
label rather than a filename. `upload_file`'s second positional parameter is
`folder_id` - never pass a filename there.
