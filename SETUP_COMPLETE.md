# Google Drive Integration - Setup Complete ✓

## Status: READY TO USE

Your last30days skill now automatically uploads research reports to Google Drive!

## What's Configured

✅ **Google Cloud OAuth Credentials**
- Location: `~/.config/last30days/gdrive_credentials.json`
- Project: my-drive-mcp-487315
- Client Type: Desktop app

✅ **Access Token**
- Location: `~/.config/last30days/gdrive_token.json`
- Status: Active and authorized
- Auto-refreshes when needed

✅ **Google Drive Folder**
- Name: "30 Day Skills"
- Auto-created on first upload
- All reports go here

## How It Works

When you run `/last30days "topic"`:

1. **Research runs** - Collects data from Reddit, X, and Web
2. **Reports generated**:
   - `report.json` - Raw data
   - `report.md` - Markdown format
   - `report.txt` - **Plain text** ← uploaded to Google Drive
   - `last30days.context.md` - Context snippet
3. **Local save** - All files saved to `~/.local/share/last30days/out/`
4. **Google Drive upload** - `report.txt` automatically uploaded to "30 Day Skills" folder
5. **Console output** - Shows upload status

## Example Output

```
[UPLOAD] Uploading report to Google Drive...
[OK] Uploaded to Google Drive: 30 Day Skills/report.txt
```

## File Locations

### Local Files
```
~/.local/share/last30days/out/
├── report.json
├── report.md
├── report.txt          ← This gets uploaded
└── last30days.context.md
```

### Google Drive
```
Google Drive/
└── 30 Day Skills/      ← Auto-created
    └── report.txt      ← Plain text, readable in browser
```

### Configuration
```
~/.config/last30days/
├── .env                      ← API keys (OPENAI_API_KEY, XAI_API_KEY)
├── gdrive_credentials.json   ← OAuth client
└── gdrive_token.json         ← Access token (auto-refreshed)
```

## Testing

**Test file uploaded**: ✓
- File: `test_last30days_upload.txt`
- Location: Google Drive > "30 Day Skills" folder
- Status: Visible and accessible

## Usage

Just use the skill normally:

```bash
/last30days "AI automation tools"
```

The report will automatically:
- Save locally
- Upload to Google Drive
- Show confirmation in output

## Troubleshooting

### If Upload Fails

**Check credentials:**
```bash
cd ~/.claude/skills/last30days
python3 setup_gdrive.py
```

Should show:
```
[OK] Google Drive is already configured!
    Credentials: ~/.config/last30days/gdrive_credentials.json
    Token: ~/.config/last30days/gdrive_token.json
```

**If token expired:**
- Delete `~/.config/last30days/gdrive_token.json`
- Next upload will re-authorize (browser opens once)

**If credentials missing:**
- Recreate OAuth client in Google Cloud Console
- Download JSON → save as `gdrive_credentials.json`

## Features

✅ Automatic upload after each research query
✅ Plain text format (readable in Google Drive)
✅ Updates existing file (no duplicates)
✅ Non-fatal errors (local copy always saves)
✅ Auto-creates "30 Day Skills" folder
✅ Token auto-refresh (no re-auth needed)

## Security

- OAuth 2.0 authentication
- Limited scope: `drive.file` (only accesses files it creates)
- Credentials stored locally only
- Token auto-refreshes securely
- Revoke access anytime: https://myaccount.google.com/permissions

## Next Steps

**You're all set!** Just use `/last30days` as normal and reports will automatically upload to Google Drive.

**Optional**: Set up API keys for better research results
- `OPENAI_API_KEY` → Reddit research
- `XAI_API_KEY` → X/Twitter research
- Edit `~/.config/last30days/.env` to add keys

---

Setup completed: 2026-02-15
Integration status: ✓ WORKING
Test upload: ✓ SUCCESSFUL
