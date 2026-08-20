#!/usr/bin/env python3
"""Interactive setup for the last30days Google Drive integration.

Verifies dependencies, checks for OAuth client credentials, runs the consent
flow to mint a token, and confirms the whole path works with a real upload.

Usage:
    python setup_gdrive.py            # run setup / verify existing setup
    python setup_gdrive.py --check    # report status only, no browser, no upload
    python setup_gdrive.py --reset    # delete the cached token and re-authorize
"""

from __future__ import annotations

import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

DEPS = [
    "google-api-python-client",
    "google-auth-httplib2",
    "google-auth-oauthlib",
]


def line(text: str = "") -> None:
    # ASCII only: this runs on Windows consoles using cp1252.
    print(text)


def header(text: str) -> None:
    line()
    line(text)
    line("=" * len(text))


def fail(text: str) -> int:
    line()
    line("[!] " + text)
    return 1


def main() -> int:
    args = set(sys.argv[1:])
    check_only = "--check" in args
    reset = "--reset" in args

    header("last30days - Google Drive setup")

    try:
        from lib import gdrive
    except ImportError as exc:
        return fail(
            "Could not import lib.gdrive from the skill's scripts directory.\n"
            "    Expected: %s\n"
            "    Error: %s"
            % (Path(__file__).resolve().parent / "scripts" / "lib" / "gdrive.py", exc)
        )

    # Step 1: dependencies
    line()
    line("1. Python dependencies")
    if not gdrive.GDRIVE_AVAILABLE:
        line("   [MISSING] Google API client libraries are not installed.")
        line()
        line("   Install them with:")
        line("     " + sys.executable + " -m pip install " + " ".join(DEPS))
        return 1
    line("   [OK] google-api-python-client, google-auth-oauthlib present")

    # Step 2: OAuth client credentials
    line()
    line("2. OAuth client credentials")
    if not gdrive.CREDENTIALS_FILE.exists():
        line("   [MISSING] " + str(gdrive.CREDENTIALS_FILE))
        line(gdrive.get_setup_instructions())
        return 1
    line("   [OK] " + str(gdrive.CREDENTIALS_FILE))

    # Step 3: token
    line()
    line("3. Access token")
    if reset and gdrive.TOKEN_FILE.exists():
        gdrive.TOKEN_FILE.unlink()
        line("   [RESET] Deleted cached token; you will be asked to re-authorize.")

    if check_only:
        if gdrive.TOKEN_FILE.exists():
            line("   [OK] Cached token at " + str(gdrive.TOKEN_FILE))
        else:
            line("   [NONE] No cached token. Run without --check to authorize.")
        line()
        line("Configured: " + ("yes" if gdrive.is_configured() else "no"))
        return 0

    if not gdrive.TOKEN_FILE.exists():
        line("   No cached token. A browser window will open for Google sign-in.")
        line("   Grant access, then return here.")

    creds = gdrive.get_credentials()
    if not creds:
        return fail(
            "Authorization failed. Delete %s and try again, or re-download the\n"
            "    OAuth client JSON if the client was deleted in Google Cloud Console."
            % gdrive.TOKEN_FILE
        )
    line("   [OK] Token valid, saved to " + str(gdrive.TOKEN_FILE))

    # Step 4: tighten permissions on the secrets (best effort, POSIX only)
    for secret in (gdrive.CREDENTIALS_FILE, gdrive.TOKEN_FILE):
        try:
            secret.chmod(0o600)
        except (OSError, NotImplementedError):
            pass

    # Step 5: end-to-end upload test
    line()
    line("4. Upload test")
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tmp_dir = Path(tempfile.mkdtemp(prefix="last30days-gdrive-"))
    probe = tmp_dir / "last30days_setup_test.txt"
    probe.write_text(
        "last30days Google Drive setup test\nWritten: %s\n"
        "Safe to delete this file.\n" % stamp,
        encoding="utf-8",
    )

    file_id = gdrive.upload_report(probe, "setup test")
    probe.unlink(missing_ok=True)
    try:
        tmp_dir.rmdir()
    except OSError:
        pass

    if not file_id:
        return fail(
            "Upload test failed. Credentials look valid, so this is usually the\n"
            "    Drive API not being enabled for the project. Enable it at\n"
            "    https://console.cloud.google.com/apis/library/drive.googleapis.com"
        )

    header("Setup complete")
    line("Reports will upload to the '%s' folder in your Google Drive." % gdrive.FOLDER_NAME)
    line("Re-running a topic updates the existing file instead of duplicating it.")
    line()
    line("A test file named 'last30days_setup_test.txt' was uploaded. You can delete it.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        line()
        line("Cancelled.")
        sys.exit(130)
