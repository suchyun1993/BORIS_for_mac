#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

export PATH="/opt/anaconda3/envs/boris/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export QT_AUTO_SCREEN_SCALE_FACTOR=1

export BORIS_APP_NAME="BORIS_for_Mac"
export BORIS_CONFIG_PATH="$HOME/.boris_for_mac"
export BORIS_RECENT_PROJECTS_PATH="$HOME/.boris_for_mac-recent-projects"
export BORIS_MPV_SOCKET_PREFIX="/tmp/boris-for-mac-mpvsocket"
export BORIS_PLAYER_MODE="qtffmpeg"
export BORIS_SKIP_PLAYER_DOCK_RESTORE="1"
export BORIS_EXTERNAL_MPV_WINDOW_TITLE_PREFIX="BORIS_for_Mac"
export BORIS_EXTERNAL_MPV_GEOMETRY="50%:50%"
export BORIS_EXTERNAL_MPV_AUTOFIT="70%x70%"
export BORIS_EXTERNAL_MPV_ONTOP="0"
export BORIS_EXTERNAL_MPV_NO_BORDER="0"

exec /opt/anaconda3/envs/boris/bin/python -m boris "$@"
