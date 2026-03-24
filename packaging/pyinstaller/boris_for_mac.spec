# -*- mode: python ; coding: utf-8 -*-

from __future__ import annotations

import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


spec_dir = Path(globals().get("SPECPATH", Path.cwd())).resolve()
project_root = spec_dir.parents[1]
src_root = project_root / "src"

sys.path.insert(0, str(src_root))

product_name = os.environ.get("BORIS_PRODUCT_NAME", "BORIS_for_Mac")
bundle_identifier = os.environ.get("BORIS_BUNDLE_IDENTIFIER", "com.yun.boris-for-mac")
release_version = os.environ.get("BORIS_RELEASE_VERSION", "0.0.0")
icon_path = os.environ.get("BORIS_ICON_PATH", "").strip()

entry_script = spec_dir / "boris_for_mac_entry.py"
runtime_hook = spec_dir / "runtime_env.py"

datas = collect_data_files("boris", include_py_files=True)
hiddenimports = collect_submodules("boris")
binaries = []

for candidate in (
    "/opt/homebrew/bin/ffmpeg",
    "/opt/homebrew/bin/ffprobe",
    "/usr/local/bin/ffmpeg",
    "/usr/local/bin/ffprobe",
):
    candidate_path = Path(candidate)
    if candidate_path.is_file():
        binaries.append((str(candidate_path), "ffmpeg-bin"))

a = Analysis(
    [str(entry_script)],
    pathex=[str(src_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[str(runtime_hook)],
    excludes=["tkinter"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=product_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name=product_name,
)

app_info = {
    "CFBundleDisplayName": product_name,
    "CFBundleName": product_name,
    "CFBundleIdentifier": bundle_identifier,
    "CFBundleShortVersionString": release_version,
    "CFBundleVersion": release_version,
    "LSMinimumSystemVersion": "12.0",
    "LSApplicationCategoryType": "public.app-category.education",
    "NSHighResolutionCapable": True,
}

app = BUNDLE(
    coll,
    name=f"{product_name}.app",
    icon=icon_path if icon_path and Path(icon_path).is_file() else None,
    bundle_identifier=bundle_identifier,
    info_plist=app_info,
)
