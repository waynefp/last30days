## LOCAL TEXT REPORT + GOOGLE DRIVE (local customization, not upstream)

**This section is a local addition to the upstream skill. It runs AFTER the synthesis is displayed and after any HTML brief flow, and it never replaces or modifies the engine's own saved artifact.**

### Relationship to the engine's saved files (read this before writing anything)

Three distinct artifacts exist. Do not conflate them:

| Artifact | Who writes it | Where | Purpose |
|---|---|---|---|
| `{slug}-raw.md` | the engine, via `--save-dir` | `LAST30DAYS_MEMORY_DIR` | raw research data; indexed by `library search` / `library feed` / `## From your library` |
| `{Topic}_Research.txt` | YOU, in this section | user's current working directory | polished, human-readable standalone report |
| `.html` brief | the HTML flow above | per `references/save-html-brief.md` | shareable doc, only when requested |

**Never write the `.txt` into `LAST30DAYS_MEMORY_DIR`, and never edit or re-render the engine's `-raw.md`.** The library indexer owns that directory. Writing a second file per run into it pollutes `library search` results and the `## From your library` context block with near-duplicate entries. Step 2.5's WebSearch appendix is the ONLY sanctioned write into the engine's raw file.

### Create the text report (mandatory unless the user opts out)

**Write a detailed `.txt` report to the user's current working directory**, unless the user explicitly said not to.

**File naming:** main topic keywords, Title_Case with underscores, e.g. `Agentforce_Certification_Research.txt`, `AI_Video_Tools_Research.txt`.

**Content:**

- Executive summary of key findings
- Detailed breakdown by insight cluster (mirror the cluster structure of the synthesis)
- Specific data from every source that returned results, with engagement numbers
- Actionable next steps and recommendations
- Source citations with engagement metrics
- Strategic insights and patterns identified

**Format:**

- Plain text (`.txt`) for maximum compatibility
- Clearly structured with headers and sections
- **No emoji and no non-ASCII punctuation.** This host is Windows with a cp1252 console; em-dashes, curly quotes, and emoji raise `UnicodeEncodeError` on write or on later `type`/`cat`. Use ASCII hyphens and straight quotes.
- Comprehensive enough to stand alone without the terminal output

### Upload to Google Drive (optional, silent when unconfigured)

**After the `.txt` is written**, attempt the upload. This is best-effort: the local file is already saved, so any failure here is non-fatal and must not interrupt the response.

```bash
"${LAST30DAYS_PYTHON:-python3}" -c "
import sys
from pathlib import Path
sys.path.insert(0, r'${SKILL_DIR}/scripts')
from lib import gdrive

report = Path(r'<absolute-path-to-the-txt-report>')
if gdrive.is_configured():
    file_id = gdrive.upload_report(report, '<topic>')
    print('Google Drive: uploaded' if file_id else 'Google Drive: upload failed (saved locally)')
else:
    print('Google Drive: not configured, saved locally only')
"
```

**Call contract - get this right:**

- `upload_report(path, topic)` takes a **`Path`**, not a `str`. Passing a `str` raises `AttributeError` on `.exists()`.
- The second parameter is the **topic label for logging**. It is NOT a filename. The uploaded name always comes from `path.name`.
- Do not call `upload_file(path, 'Some_Name.txt')` - `upload_file`'s second positional parameter is `folder_id`, and passing a filename there sends a bogus folder ID to the Drive API.

**Behavior:**

- Uploads to the `30 Day Skills` folder, created on first use
- Same-name files are updated in place, so re-running a topic will not create duplicates
- If Drive is not configured, skip silently. Do NOT prompt the user to set it up unless they ask.
- Report the outcome in one short line at the end of your response, not as a section

**Setup, only if the user asks:** `python ~/.claude/skills/last30days/setup_gdrive.py`

---

