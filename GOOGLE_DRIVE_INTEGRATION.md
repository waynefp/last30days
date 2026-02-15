# Google Drive Integration - Implementation Summary

## What Was Implemented

The `last30days` skill now automatically uploads research reports to Google Drive in addition to saving them locally.

## Key Features

✅ **Automatic Upload** - Reports upload to "30 Day Skills" folder after each research query
✅ **Plain Text Format** - Saves as .txt files (readable in Google Drive, not .md)
✅ **Local + Cloud** - Files saved both locally AND to Google Drive
✅ **Update in Place** - Existing reports are updated, not duplicated
✅ **Graceful Fallback** - If upload fails, local copy still saves
✅ **Optional** - Works with or without Google Drive configured

## Files Created/Modified

### New Files
- `~/.claude/skills/last30days/scripts/lib/gdrive.py` - Google Drive API integration
- `~/.claude/skills/last30days/setup_gdrive.py` - Setup helper script
- `~/.claude/skills/last30days/GOOGLE_DRIVE_SETUP.md` - Complete setup guide

### Modified Files
- `scripts/lib/render.py` - Added .txt rendering and upload logic
- `SKILL.md` - Updated to document Google Drive feature
- `CLAUDE.md` - Added Google Drive integration section

## Setup Instructions

### Quick Setup

1. **Install dependencies:**
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

2. **View setup instructions:**
   ```bash
   cd ~/.claude/skills/last30days
   python setup_gdrive.py
   ```

3. **Follow the detailed guide:**
   - See `GOOGLE_DRIVE_SETUP.md` for complete step-by-step instructions
   - You'll need to create a Google Cloud project (one-time)
   - Download OAuth credentials
   - First run will open browser for authentication

### Check Status

```bash
cd ~/.claude/skills/last30days
python setup_gdrive.py
```

Shows whether Google Drive is configured and ready.

## How It Works

1. **Research runs** - User invokes `/last30days "topic"`
2. **Data collected** - Reddit, X, and/or Web sources scraped
3. **Reports generated:**
   - `report.json` - Raw data
   - `report.md` - Markdown format
   - `report.txt` - **Plain text (NEW)** ← uploaded to Google Drive
   - `last30days.context.md` - Context snippet
4. **Upload attempt:**
   - If `~/.config/last30days/gdrive_credentials.json` exists
   - Upload `report.txt` to "30 Day Skills/" folder
   - Update existing file or create new one
5. **Status shown:**
   - ✅ Success: "Uploaded to Google Drive: 30 Day Skills/report.txt"
   - ⚠️ Not configured: "Google Drive not configured. Run setup..."
   - ⚠️ Failed: "Google Drive upload failed: [error]"

## File Locations

### Local Files
```
~/.local/share/last30days/out/
├── report.json
├── report.md
├── report.txt          ← This gets uploaded to Google Drive
└── last30days.context.md
```

### Google Drive
```
Google Drive/
└── 30 Day Skills/      ← Auto-created folder
    └── report.txt      ← Plain text, readable in browser
```

### Configuration
```
~/.config/last30days/
├── .env                          ← API keys (existing)
├── gdrive_credentials.json       ← OAuth client (you provide)
└── gdrive_token.json             ← Access token (auto-generated)
```

## Technical Details

### Dependencies
- `google-api-python-client` - Google Drive API client
- `google-auth-httplib2` - HTTP library for auth
- `google-auth-oauthlib` - OAuth2 flow

### API Scope
- `https://www.googleapis.com/auth/drive.file` - Only access files created by the app

### Error Handling
- Upload errors are non-fatal (local file still saves)
- Token refresh is automatic
- Missing credentials silently skip upload (no error spam)

## Security

- Credentials stored locally only
- Limited scope (can't access your other Drive files)
- OAuth2 flow ensures secure authentication
- Revoke access anytime at: https://myaccount.google.com/permissions

## Testing

You can test without setting up Google Drive:
- The skill works normally without credentials
- It will show a tip about enabling Google Drive
- All reports save locally as before

## Next Steps

1. **Install dependencies** (if not already installed)
2. **Run `setup_gdrive.py`** to see current status
3. **Follow `GOOGLE_DRIVE_SETUP.md`** for complete setup
4. **Run a test query** to verify upload works

## Support

- Full setup guide: `GOOGLE_DRIVE_SETUP.md`
- Setup script: `python setup_gdrive.py`
- Code: `scripts/lib/gdrive.py`
