#!/usr/bin/env python3
"""Prompt locally for Backblaze B2 credentials and configure rclone."""

from __future__ import annotations

import subprocess
import sys
from getpass import getpass


def main() -> int:
    key_id = input("Paste Backblaze keyID, then press Enter: ").strip()
    app_key = getpass("Paste Backblaze applicationKey, then press Enter: ").strip()

    print(f"keyID length: {len(key_id)}")
    print(f"applicationKey length: {len(app_key)}")

    if not key_id or not app_key:
        print("STOP: keyID or applicationKey is empty. Start over.")
        return 1

    subprocess.run(
        ["rclone", "config", "create", "matt", "b2", "account", key_id, "key", app_key],
        check=True,
    )
    print("Remote written. Testing matt: ...")
    return subprocess.run(["rclone", "lsd", "matt:"], check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
