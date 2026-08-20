"""Google Drive upload functionality for last30days skill."""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from google.oauth2.credentials import Credentials

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False
    Credentials = None  # type: ignore

# If modifying these scopes, delete the token file.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Configuration directory
CONFIG_DIR = Path.home() / ".config" / "last30days"
CREDENTIALS_FILE = CONFIG_DIR / "gdrive_credentials.json"
TOKEN_FILE = CONFIG_DIR / "gdrive_token.json"

FOLDER_NAME = "30 Day Skills"


def is_configured() -> bool:
    """Check if Google Drive is configured with credentials."""
    return GDRIVE_AVAILABLE and CREDENTIALS_FILE.exists()


def get_credentials() -> Optional[Credentials]:
    """Get Google Drive credentials, refreshing if needed.

    Returns:
        Credentials object or None if not configured
    """
    if not GDRIVE_AVAILABLE:
        return None

    if not CREDENTIALS_FILE.exists():
        return None

    creds = None

    # Load existing token
    if TOKEN_FILE.exists():
        try:
            # Try loading as standard Google auth format
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception:
            # Try loading Google Drive MCP token format
            try:
                with open(TOKEN_FILE, 'r') as f:
                    token_data = json.load(f)

                # Load client ID and secret from credentials file
                client_id = None
                client_secret = None
                with open(CREDENTIALS_FILE, 'r') as cf:
                    cred_data = json.load(cf)
                    if 'installed' in cred_data:
                        client_id = cred_data['installed']['client_id']
                        client_secret = cred_data['installed']['client_secret']

                # Convert MCP format to google-auth format
                if 'access_token' in token_data and client_id and client_secret:
                    # MCP uses expiry_date (timestamp in ms), google-auth uses expiry (ISO string)
                    creds = Credentials(
                        token=token_data.get('access_token'),
                        refresh_token=token_data.get('refresh_token'),
                        token_uri='https://oauth2.googleapis.com/token',
                        client_id=client_id,
                        client_secret=client_secret,
                        scopes=SCOPES
                    )
            except Exception as e:
                print(f"[!] Could not load token: {e}")

    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed token
                _save_token(creds)
            except Exception as e:
                print(f"[!] Token refresh failed: {e}")
                creds = None

        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES)
                creds = flow.run_local_server(port=0)
                # Save new token
                _save_token(creds)
            except Exception as e:
                print(f"[!] Failed to authenticate with Google Drive: {e}")
                return None

    return creds


def _save_token(creds: Credentials):
    """Save credentials to token file.

    Args:
        creds: Credentials object to save
    """
    try:
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    except Exception as e:
        print(f"[!] Failed to save Google Drive token: {e}")


def find_or_create_folder(service, folder_name: str = FOLDER_NAME) -> Optional[str]:
    """Find or create the target folder in Google Drive.

    Args:
        service: Google Drive API service
        folder_name: Name of the folder to find/create

    Returns:
        Folder ID or None if failed
    """
    try:
        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=1
        ).execute()

        files = results.get('files', [])

        if files:
            return files[0]['id']

        # Create folder if it doesn't exist
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        folder = service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()

        return folder.get('id')

    except HttpError as e:
        print(f"[!] Error finding/creating Google Drive folder: {e}")
        return None


def upload_file(
    file_path: Path,
    folder_id: Optional[str] = None,
    mime_type: str = 'text/plain'
) -> Optional[str]:
    """Upload a file to Google Drive.

    Args:
        file_path: Path to the file to upload
        folder_id: ID of the folder to upload to (optional)
        mime_type: MIME type of the file

    Returns:
        File ID of uploaded file or None if failed
    """
    if not GDRIVE_AVAILABLE:
        return None

    if not file_path.exists():
        print(f"[!] File not found: {file_path}")
        return None

    try:
        creds = get_credentials()
        if not creds:
            return None

        service = build('drive', 'v3', credentials=creds)

        # Use provided folder or find/create default folder
        if folder_id is None:
            folder_id = find_or_create_folder(service)
            if not folder_id:
                print("[!] Could not find or create target folder")
                return None

        # Check if file already exists in folder
        file_name = file_path.name
        query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=1
        ).execute()

        files = results.get('files', [])

        # Prepare file metadata
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        # Upload file content
        media = MediaFileUpload(
            str(file_path),
            mimetype=mime_type,
            resumable=True
        )

        if files:
            # Update existing file
            file_id = files[0]['id']
            file = service.files().update(
                fileId=file_id,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
        else:
            # Create new file
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()

        return file.get('id')

    except HttpError as e:
        print(f"[!] Error uploading to Google Drive: {e}")
        return None
    except Exception as e:
        print(f"[!] Unexpected error uploading to Google Drive: {e}")
        return None


def upload_report(file_path: Path, topic: str) -> Optional[str]:
    """Upload a research report to Google Drive.

    Args:
        file_path: Path to the report file
        topic: Research topic (for logging)

    Returns:
        File ID if successful, None otherwise
    """
    if not is_configured():
        return None

    print(f"[UPLOAD] Uploading report to Google Drive...")

    file_id = upload_file(file_path, mime_type='text/plain')

    if file_id:
        print(f"[OK] Uploaded to Google Drive: {FOLDER_NAME}/{file_path.name}")
        return file_id
    else:
        print(f"[!] Failed to upload to Google Drive")
        return None


def get_setup_instructions() -> str:
    """Get instructions for setting up Google Drive integration.

    Returns:
        Multi-line string with setup instructions
    """
    if not GDRIVE_AVAILABLE:
        return """
Google Drive integration requires additional dependencies.
Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

    return f"""
Google Drive Setup Instructions:
=================================

1. Enable Google Drive API:
   - Go to https://console.cloud.google.com/
   - Create a new project or select existing one
   - Enable the Google Drive API
   - Go to Credentials > Create Credentials > OAuth client ID
   - Choose "Desktop app" as application type
   - Download the JSON credentials file

2. Save credentials:
   - Rename the downloaded file to: gdrive_credentials.json
   - Move it to: {CREDENTIALS_FILE}

3. First run:
   - Next time a report is generated, a browser will open
   - Sign in with your Google account
   - Grant permissions to the application
   - The token will be saved for future use

4. Done!
   - Reports will automatically upload to "{FOLDER_NAME}" folder
   - Updates to existing reports will replace the file
"""
