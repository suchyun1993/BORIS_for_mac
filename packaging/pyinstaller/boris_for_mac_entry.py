#!/usr/bin/env python3
"""
PyInstaller entry point for BORIS_for_Mac.
"""

from __future__ import annotations

import os
from pathlib import Path


def _configure_runtime_environment() -> None:
    home = Path.home()

    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    os.environ.setdefault("BORIS_APP_NAME", "BORIS_for_Mac")
    os.environ.setdefault("BORIS_CONFIG_PATH", str(home / ".boris_for_mac"))
    os.environ.setdefault("BORIS_RECENT_PROJECTS_PATH", str(home / ".boris_for_mac-recent-projects"))
    os.environ.setdefault("BORIS_MPV_SOCKET_PREFIX", "/tmp/boris-for-mac-mpvsocket")
    os.environ.setdefault("BORIS_PLAYER_MODE", "qtffmpeg")
    os.environ.setdefault("BORIS_SKIP_PLAYER_DOCK_RESTORE", "1")
    os.environ.setdefault("BORIS_EXTERNAL_MPV_WINDOW_TITLE_PREFIX", "BORIS_for_Mac")
    os.environ.setdefault("BORIS_EXTERNAL_MPV_GEOMETRY", "50%:50%")
    os.environ.setdefault("BORIS_EXTERNAL_MPV_AUTOFIT", "70%x70%")
    os.environ.setdefault("BORIS_EXTERNAL_MPV_ONTOP", "0")
    os.environ.setdefault("BORIS_EXTERNAL_MPV_NO_BORDER", "0")


def main() -> None:
    _configure_runtime_environment()
    from boris import main as boris_main

    boris_main()


if __name__ == "__main__":
    main()
