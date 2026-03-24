"""
Runtime hook used by the BORIS_for_Mac PyInstaller bundle.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

home = Path.home()
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
os.environ.setdefault("BORIS_APP_NAME", "BORIS_for_Mac")
os.environ.setdefault("BORIS_CONFIG_PATH", str(home / ".boris_for_mac"))
os.environ.setdefault("BORIS_RECENT_PROJECTS_PATH", str(home / ".boris_for_mac-recent-projects"))
os.environ.setdefault("BORIS_MPV_SOCKET_PREFIX", "/tmp/boris-for-mac-mpvsocket")
os.environ.setdefault("BORIS_PLAYER_MODE", "qtffmpeg")
os.environ.setdefault("BORIS_SKIP_PLAYER_DOCK_RESTORE", "1")
os.environ.setdefault("BORIS_EXTERNAL_MPV_WINDOW_TITLE_PREFIX", "BORIS_for_Mac")

bundle_root = Path(getattr(sys, "_MEIPASS", ""))
ffmpeg_dir = bundle_root / "ffmpeg-bin"
if ffmpeg_dir.is_dir():
    os.environ["PATH"] = f"{ffmpeg_dir}{os.pathsep}{os.environ.get('PATH', '')}"
