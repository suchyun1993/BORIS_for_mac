#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE_ROOT="$(cd "$ROOT/.." && pwd)"

PRODUCT_NAME="${BORIS_PRODUCT_NAME:-BORIS_for_Mac}"
ARCH_TAG="${BORIS_RELEASE_ARCH:-arm64}"
DIST_DIR="${DIST_DIR:-$WORKSPACE_ROOT/dist}"
STAGING_DIR="$DIST_DIR/dmg-staging-$PRODUCT_NAME"
README_SOURCE="$ROOT/packaging/DMG_README.txt"
APP_PATH="$DIST_DIR/$PRODUCT_NAME.app"

VERSION_INPUT="${1:-}"
RELEASE_VERSION="${BORIS_RELEASE_VERSION:-$VERSION_INPUT}"
RELEASE_VERSION="${RELEASE_VERSION#v}"

require_tool() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "Missing required tool: $1" >&2
        exit 1
    fi
}

require_tool hdiutil
require_tool shasum
require_tool /usr/libexec/PlistBuddy

if [[ -z "$RELEASE_VERSION" ]]; then
    RELEASE_VERSION="$("$ROOT/scripts/build_boris_for_mac_app.sh" | awk -F': ' '/Release version/{print $2}' | tail -n 1)"
else
    "$ROOT/scripts/build_boris_for_mac_app.sh" "$RELEASE_VERSION"
fi

if [[ -z "$RELEASE_VERSION" ]]; then
    echo "Unable to determine release version for DMG build." >&2
    exit 1
fi

if [[ ! -d "$APP_PATH" ]]; then
    echo "App bundle not found at $APP_PATH" >&2
    exit 1
fi

DMG_FILENAME="${PRODUCT_NAME}-${RELEASE_VERSION}-${ARCH_TAG}.dmg"
DMG_PATH="$DIST_DIR/$DMG_FILENAME"
VOLUME_NAME="$PRODUCT_NAME"

rm -rf "$STAGING_DIR" "$DMG_PATH"
mkdir -p "$STAGING_DIR"

cp -R "$APP_PATH" "$STAGING_DIR/$PRODUCT_NAME.app"
if [[ -f "$README_SOURCE" ]]; then
    cp "$README_SOURCE" "$STAGING_DIR/README.txt"
fi
ln -s /Applications "$STAGING_DIR/Applications"

for plist in \
    "$APP_PATH/Contents/Info.plist" \
    "$STAGING_DIR/$PRODUCT_NAME.app/Contents/Info.plist"; do
    if [[ -f "$plist" ]]; then
        /usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName $PRODUCT_NAME" "$plist" || true
        /usr/libexec/PlistBuddy -c "Set :CFBundleName $PRODUCT_NAME" "$plist" || true
        /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $RELEASE_VERSION" "$plist" || true
        /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $RELEASE_VERSION" "$plist" || true
    fi
done

hdiutil create \
    -volname "$VOLUME_NAME" \
    -srcfolder "$STAGING_DIR" \
    -ov \
    -format UDZO \
    "$DMG_PATH" || {
    echo "hdiutil create failed once, retrying without Applications symlink..."
    rm -f "$STAGING_DIR/Applications"
    hdiutil create \
        -volname "$VOLUME_NAME" \
        -srcfolder "$STAGING_DIR" \
        -ov \
        -format UDZO \
        "$DMG_PATH"
}

echo "Created DMG: $DMG_PATH"
echo "SHA256: $(shasum -a 256 "$DMG_PATH" | awk '{print $1}')"
