#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE_ROOT="$(cd "$ROOT/.." && pwd)"

PYTHON_BIN="${PYTHON_BIN:-/opt/anaconda3/envs/boris/bin/python}"
PRODUCT_NAME="${BORIS_PRODUCT_NAME:-BORIS_for_Mac}"
BUNDLE_IDENTIFIER="${BORIS_BUNDLE_IDENTIFIER:-com.yun.boris-for-mac}"
SPEC_PATH="$ROOT/packaging/pyinstaller/boris_for_mac.spec"
DIST_DIR="${DIST_DIR:-$WORKSPACE_ROOT/dist}"
WORK_DIR="${PYINSTALLER_WORK_DIR:-$WORKSPACE_ROOT/build/pyinstaller}"
PYINSTALLER_CONFIG_DIR="${PYINSTALLER_CONFIG_DIR:-$WORKSPACE_ROOT/.pyinstaller}"
MPLCONFIGDIR="${MPLCONFIGDIR:-$WORKSPACE_ROOT/.mplconfig}"

VERSION_INPUT="${1:-}"
RELEASE_VERSION="${BORIS_RELEASE_VERSION:-$VERSION_INPUT}"
RELEASE_VERSION="${RELEASE_VERSION#v}"

require_tool() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "Missing required tool: $1" >&2
        exit 1
    fi
}

if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Python not found or not executable: $PYTHON_BIN" >&2
    exit 1
fi

if [[ -z "$RELEASE_VERSION" ]]; then
    export BORIS_SOURCE_ROOT="$ROOT"
    RELEASE_VERSION="$(
        "$PYTHON_BIN" - <<'PY'
import pathlib
import re
import os

source_root = pathlib.Path(os.environ["BORIS_SOURCE_ROOT"])
version_file = source_root / "src" / "boris" / "version.py"
text = version_file.read_text(encoding="utf-8")
match = re.search(r'__version__\s*=\s*"([^"]+)"', text)
print(match.group(1) if match else "0.0.0")
PY
    )"
fi

if [[ -z "$RELEASE_VERSION" ]]; then
    echo "Unable to determine release version." >&2
    exit 1
fi

ICON_PATH=""
for candidate in \
    "$ROOT/packaging/AppIcon.icns" \
    "$WORKSPACE_ROOT/dist/Boris_V2.0.app/Contents/Resources/AppIcon.icns" \
    "$WORKSPACE_ROOT/dist/BORIS_for_Mac.app/Contents/Resources/AppIcon.icns"; do
    if [[ -f "$candidate" ]]; then
        ICON_PATH="$candidate"
        break
    fi
done

if ! "$PYTHON_BIN" -c "import PyInstaller" >/dev/null 2>&1; then
    echo "PyInstaller not found in $PYTHON_BIN; installing into this environment..."
    "$PYTHON_BIN" -m pip install --upgrade pyinstaller
fi

require_tool /usr/libexec/PlistBuddy

mkdir -p "$DIST_DIR" "$WORK_DIR"
mkdir -p "$PYINSTALLER_CONFIG_DIR" "$MPLCONFIGDIR"

export BORIS_RELEASE_VERSION="$RELEASE_VERSION"
export BORIS_PRODUCT_NAME="$PRODUCT_NAME"
export BORIS_BUNDLE_IDENTIFIER="$BUNDLE_IDENTIFIER"
export BORIS_ICON_PATH="$ICON_PATH"
export PYINSTALLER_CONFIG_DIR
export MPLCONFIGDIR

"$PYTHON_BIN" -m PyInstaller \
    --noconfirm \
    --clean \
    --distpath "$DIST_DIR" \
    --workpath "$WORK_DIR" \
    "$SPEC_PATH"

APP_PATH="$DIST_DIR/$PRODUCT_NAME.app"
INFO_PLIST="$APP_PATH/Contents/Info.plist"

if [[ ! -d "$APP_PATH" ]]; then
    echo "Build failed: app not found at $APP_PATH" >&2
    exit 1
fi

if [[ -f "$INFO_PLIST" ]]; then
    /usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName $PRODUCT_NAME" "$INFO_PLIST" || true
    /usr/libexec/PlistBuddy -c "Set :CFBundleName $PRODUCT_NAME" "$INFO_PLIST" || true
    /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $RELEASE_VERSION" "$INFO_PLIST" || true
    /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $RELEASE_VERSION" "$INFO_PLIST" || true
fi

echo "Built app: $APP_PATH"
echo "Release version: $RELEASE_VERSION"
