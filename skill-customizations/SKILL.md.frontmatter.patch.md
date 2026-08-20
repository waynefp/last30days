# SKILL.md frontmatter customizations

Two one-line edits in the YAML frontmatter of
`~/.claude/skills/last30days/SKILL.md`. Both are overwritten by every upstream
merge and are easy to overlook, since they sit far from the `## LOCAL TEXT REPORT`
section that is the more obvious customization.

## 1. Version suffix

Append `+gdrive` to the upstream version so the badge and `doctor` make it obvious
this install is not stock.

```yaml
# upstream
version: "3.21.1"

# customized
version: "3.21.1+gdrive"
```

The numeric part tracks whatever upstream release is installed; only the `+gdrive`
suffix is local. After merging 3.22.0, the line becomes `"3.22.0+gdrive"`.

## 2. Description sentence

Append one sentence to the end of the `description:` value, before the closing
quote. The rest of the string must stay byte-identical to upstream.

Appended text:

```
 Saves a polished .txt report to CWD and optionally uploads it to Google Drive.
```

Full customized line for 3.21.1:

```yaml
description: "Research what people actually say about any topic in the last 30 days. Pulls posts and engagement from Reddit, X, YouTube, TikTok, Hacker News, Polymarket, GitHub, and the web. Includes a doctor health check to diagnose broken or missing sources. Saves a polished .txt report to CWD and optionally uploads it to Google Drive."
```

This sentence is what surfaces in the skill picker, so if the listing stops
mentioning Google Drive, this edit was lost.

## Verifying both

```bash
cd ~/.claude/skills/last30days
sed -n '3p' SKILL.md                                  # expect ...+gdrive
sed -n '4p' SKILL.md | grep -c "uploads it to Google Drive"   # expect 1
```

Note the description line ends `Google Drive."` — a trailing-anchored grep for
`Google Drive$` will fail because of the closing quote.
