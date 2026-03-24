#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE_ROOT="$(cd "$ROOT/.." && pwd)"
TAP_DIR="${TAP_DIR:-$WORKSPACE_ROOT/homebrew-boris-for-mac}"
CASK_PATH="$TAP_DIR/Casks/boris-for-mac.rb"

VERSION_INPUT="${1:-}"
ARG2="${2:-}"
ARG3="${3:-}"

GITHUB_OWNER=""
GITHUB_REPO=""

if [[ -n "$ARG3" ]]; then
    GITHUB_OWNER="$ARG2"
    GITHUB_REPO="$ARG3"
elif [[ "$ARG2" == */* ]]; then
    GITHUB_OWNER="${ARG2%%/*}"
    GITHUB_REPO="${ARG2##*/}"
fi

if [[ -z "$VERSION_INPUT" || -z "$GITHUB_OWNER" || -z "$GITHUB_REPO" ]]; then
    echo "Usage: $0 <version> <github_owner> <github_repo>" >&2
    echo "   or: $0 <version> <github_owner>/<github_repo>" >&2
    exit 1
fi

VERSION="${VERSION_INPUT#v}"
DMG_PATH="$WORKSPACE_ROOT/dist/BORIS_for_Mac-$VERSION-arm64.dmg"

if [[ ! -f "$DMG_PATH" ]]; then
    echo "DMG not found: $DMG_PATH" >&2
    exit 1
fi

SHA256="$(shasum -a 256 "$DMG_PATH" | awk '{print $1}')"

mkdir -p "$(dirname "$CASK_PATH")"
cat > "$CASK_PATH" <<EOF
cask "boris-for-mac" do
  arch arm: "arm64"

  version "$VERSION"
  sha256 arm: "$SHA256"

  url "https://github.com/$GITHUB_OWNER/$GITHUB_REPO/releases/download/v#{version}/BORIS_for_Mac-#{version}-#{arch}.dmg"
  name "BORIS_for_Mac"
  desc "BORIS embedded-video macOS build"
  homepage "https://github.com/$GITHUB_OWNER/$GITHUB_REPO"

  depends_on arch: :arm64
  depends_on formula: "ffmpeg"
  depends_on macos: ">= :monterey"

  app "BORIS_for_Mac.app"

  zap trash: [
    "~/.boris_for_mac",
    "~/.boris_for_mac-recent-projects",
  ]
end
EOF

echo "Updated cask at $CASK_PATH"
echo "version=$VERSION"
echo "sha256=$SHA256"
