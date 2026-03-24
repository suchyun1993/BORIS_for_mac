#!/bin/bash
set -euo pipefail

echo "build_boris_v2_dmg.sh is deprecated. Redirecting to BORIS_for_Mac build script..."
exec "$(cd "$(dirname "$0")" && pwd)/build_boris_for_mac_dmg.sh" "$@"
