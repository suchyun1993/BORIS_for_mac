"""
BORIS
Behavioral Observation Research Interactive Software
Copyright 2012-2026 Olivier Friard

This file is part of BORIS.

  BORIS is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  any later version.

  BORIS is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not see <http://www.gnu.org/licenses/>.

"""

import json
import os
import socket
import subprocess
import tempfile
import time
from pathlib import Path

import PIL.Image

import logging
import config as cfg

logger = logging.getLogger(__name__)


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class _NullOverlay:
    def update(self, *_args, **_kwargs):
        return

    def remove(self):
        return


class IPC_MPV:
    """
    class for managing mpv through Inter Process Communication (IPC)
    """

    media_durations: list = []
    cumul_media_durations: list = []
    fps: list = []
    _pause: bool = False

    def __init__(self, socket_path: str = cfg.MPV_SOCKET, parent=None, player_id: int | None = None, window_title: str | None = None):
        self.socket_path = socket_path
        self.parent = parent
        self.player_id = player_id
        self.process = None
        self.window_title = window_title or self._default_window_title()
        self._volume = 50
        self._image_display_duration = 1
        self._hwdec = cfg.MPV_HWDEC_DEFAULT_VALUE
        self.log_handler = None
        self.init_mpv()

    def _default_window_title(self) -> str:
        if self.player_id is None:
            return cfg.programName
        prefix = os.environ.get("BORIS_EXTERNAL_MPV_WINDOW_TITLE_PREFIX", cfg.programName)
        return f"{prefix} - Player #{self.player_id + 1}"

    def _remove_socket_file(self) -> None:
        socket_file = Path(self.socket_path)
        if socket_file.exists():
            socket_file.unlink()

    def _spawn_args(self) -> list[str]:
        args = [
            "mpv",
            "--osc=no",
            f"--input-ipc-server={self.socket_path}",
            "--idle=yes",
            "--keep-open=always",
            "--force-window=yes",
            "--input-default-bindings=no",
            "--input-vo-keyboard=no",
            f"--title={self.window_title}",
            f"--geometry={os.environ.get('BORIS_EXTERNAL_MPV_GEOMETRY', '50%:50%')}",
            f"--autofit-larger={os.environ.get('BORIS_EXTERNAL_MPV_AUTOFIT', '70%x70%')}",
            f"--ontop={'yes' if _env_flag('BORIS_EXTERNAL_MPV_ONTOP', False) else 'no'}",
        ]

        if _env_flag("BORIS_EXTERNAL_MPV_NO_BORDER", False):
            args.append("--no-border")

        return args

    def init_mpv(self) -> None:
        """
        Start mpv process managed through IPC.
        """

        self._remove_socket_file()
        logger.info(f"Start mpv ipc process socket={self.socket_path} title={self.window_title}")
        self.process = subprocess.Popen(
            self._spawn_args(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.wait_until_ready()

    def wait_until_ready(self, timeout: float = 5.0) -> bool:
        deadline = time.time() + timeout
        socket_file = Path(self.socket_path)

        while time.time() < deadline:
            if self.process is not None and self.process.poll() is not None:
                logger.warning(f"mpv process exited early for socket={self.socket_path}")
                return False
            if socket_file.exists():
                return True
            time.sleep(0.1)

        logger.warning(f"Timed out waiting for mpv IPC socket={self.socket_path}")
        return False

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def restart(self) -> bool:
        logger.warning(f"Respawn mpv ipc process socket={self.socket_path}")
        self.terminate()
        self.init_mpv()
        return self.wait_until_ready()

    def terminate(self) -> None:
        if self.process is not None:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as exc:
                logger.warning(f"Error terminating mpv process socket={self.socket_path}: {exc}")
            finally:
                self.process = None

        self._remove_socket_file()

    def _ensure_process(self) -> bool:
        if self.is_running() and Path(self.socket_path).exists():
            return True
        return self.restart()

    def _send_command_once(self, command):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(2)
            client.connect(self.socket_path)
            client.sendall(json.dumps(command).encode("utf-8") + b"\n")
            response = client.recv(4096)
            response_data = json.loads(response.decode("utf-8"))
            if response_data["error"] != "success":
                logging.warning(f"send command: {command} response data: {response_data}")
            return response_data.get("data")

    def send_command(self, command):
        """
        Send a JSON command to the MPV IPC server.
        """

        if not self._ensure_process():
            logger.critical(f"Unable to ensure mpv process for socket={self.socket_path}")
            return None

        for attempt in range(2):
            try:
                return self._send_command_once(command)
            except (FileNotFoundError, ConnectionRefusedError, socket.timeout, json.JSONDecodeError, OSError) as exc:
                logger.warning(f"mpv IPC command failed attempt={attempt + 1} socket={self.socket_path}: {exc}")
                if attempt == 0 and self.restart():
                    continue
                break

        return None

    def set_window_title(self, title: str) -> None:
        self.window_title = title
        self.send_command({"command": ["set_property", "title", title]})

    def ensure_window(self, title: str | None = None) -> None:
        if title:
            self.set_window_title(title)
        self.send_command({"command": ["set_property", "force-window", "yes"]})
        self.send_command({"command": ["set_property", "ontop", False]})
        self.send_command({"command": ["set_property", "fullscreen", False]})
        self.send_command({"command": ["set_property", "window-minimized", False]})
        self.send_command({"command": ["set_property", "keep-open", "always"]})

    @property
    def time_pos(self):
        return self.send_command({"command": ["get_property", "time-pos"]})

    @property
    def duration(self):
        return self.send_command({"command": ["get_property", "duration"]})

    @property
    def video_zoom(self):
        return self.send_command({"command": ["get_property", "video-zoom"]})

    @video_zoom.setter
    def video_zoom(self, value):
        self.send_command({"command": ["set_property", "video-zoom", value]})

    @property
    def pause(self):
        return self.send_command({"command": ["get_property", "pause"]})

    @pause.setter
    def pause(self, value):
        self.send_command({"command": ["set_property", "pause", value]})

    @property
    def estimated_frame_number(self):
        return self.send_command({"command": ["get_property", "estimated-frame-number"]})

    def stop(self):
        self.send_command({"command": ["stop"]})

    @property
    def playlist(self):
        return self.send_command({"command": ["get_property", "playlist"]})

    def playlist_next(self):
        self.send_command({"command": ["playlist-next"]})

    def playlist_prev(self):
        self.send_command({"command": ["playlist-prev"]})

    @property
    def playlist_pos(self):
        return self.send_command({"command": ["get_property", "playlist-pos"]})

    @playlist_pos.setter
    def playlist_pos(self, value):
        self.send_command({"command": ["set_property", "playlist-pos", value]})

    @property
    def playlist_count(self):
        return self.send_command({"command": ["get_property", "playlist-count"]})

    def loadfile(self, media, mode: str = "replace"):
        return self.send_command({"command": ["loadfile", media, mode]})

    def playlist_append(self, media):
        return self.loadfile(media, "append")

    def playlist_replace(self, media):
        return self.loadfile(media, "replace")

    def wait_until_playing(self):
        self.wait_until_ready()

    def prime_frame(self, seek_time: float = 0.0) -> None:
        """
        Warm up the external mpv window so the first visible frame is rendered
        instead of leaving the window black on initial load.
        """

        self.ensure_window()
        self.pause = False

        deadline = time.time() + 1.5
        while time.time() < deadline:
            if self.video_format:
                break
            time.sleep(0.05)

        time.sleep(0.15)
        self.pause = True
        self.seek(seek_time, "absolute+exact")

    def seek(self, value, mode: str):
        self.send_command({"command": ["seek", value, mode]})

    @property
    def playback_time(self):
        return self.send_command({"command": ["get_property", "playback-time"]})

    def frame_step(self):
        self.send_command({"command": ["frame-step"]})

    def frame_back_step(self):
        self.send_command({"command": ["frame-back-step"]})

    def screenshot_to_file(self, value):
        self.send_command({"command": ["screenshot-to-file", value, "video"]})

    def screenshot_raw(self):
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        temp_file.close()
        try:
            self.screenshot_to_file(temp_file.name)
            deadline = time.time() + 2
            while time.time() < deadline:
                if Path(temp_file.name).exists() and Path(temp_file.name).stat().st_size > 0:
                    with PIL.Image.open(temp_file.name) as img:
                        return img.copy()
                time.sleep(0.1)
        finally:
            Path(temp_file.name).unlink(missing_ok=True)

        raise RuntimeError("Unable to capture screenshot from mpv IPC player")

    @property
    def speed(self):
        return self.send_command({"command": ["get_property", "speed"]})

    @speed.setter
    def speed(self, value):
        self.send_command({"command": ["set_property", "speed", value]})

    @property
    def video_rotate(self):
        return self.send_command({"command": ["get_property", "video-rotate"]})

    @video_rotate.setter
    def video_rotate(self, value):
        self.send_command({"command": ["set_property", "video-rotate", value]})

    @property
    def sub_visibility(self):
        return self.send_command({"command": ["get_property", "sub-visibility"]})

    @sub_visibility.setter
    def sub_visibility(self, value):
        self.send_command({"command": ["set_property", "sub-visibility", value]})

    @property
    def brightness(self):
        return self.send_command({"command": ["get_property", "brightness"]})

    @brightness.setter
    def brightness(self, value):
        self.send_command({"command": ["set_property", "brightness", value]})

    @property
    def contrast(self):
        return self.send_command({"command": ["get_property", "contrast"]})

    @contrast.setter
    def contrast(self, value):
        self.send_command({"command": ["set_property", "contrast", value]})

    @property
    def saturation(self):
        return self.send_command({"command": ["get_property", "saturation"]})

    @saturation.setter
    def saturation(self, value):
        self.send_command({"command": ["set_property", "saturation", value]})

    @property
    def gamma(self):
        return self.send_command({"command": ["get_property", "gamma"]})

    @gamma.setter
    def gamma(self, value):
        self.send_command({"command": ["set_property", "gamma", value]})

    @property
    def hue(self):
        return self.send_command({"command": ["get_property", "hue"]})

    @hue.setter
    def hue(self, value):
        self.send_command({"command": ["set_property", "hue", value]})

    @property
    def container_fps(self):
        return self.send_command({"command": ["get_property", "container-fps"]})

    @property
    def width(self):
        return self.send_command({"command": ["get_property", "width"]})

    @property
    def height(self):
        return self.send_command({"command": ["get_property", "height"]})

    @property
    def video_format(self):
        return self.send_command({"command": ["get_property", "video-format"]})

    @property
    def deinterlace(self):
        return self.send_command({"command": ["get_property", "deinterlace"]})

    @deinterlace.setter
    def deinterlace(self, value):
        self.send_command({"command": ["set_property", "deinterlace", value]})

    @property
    def audio_bitrate(self):
        return self.send_command({"command": ["get_property", "audio-bitrate"]})

    @property
    def volume(self):
        value = self.send_command({"command": ["get_property", "volume"]})
        return self._volume if value is None else value

    @volume.setter
    def volume(self, value):
        self._volume = value
        self.send_command({"command": ["set_property", "volume", value]})

    @property
    def mute(self):
        value = self.send_command({"command": ["get_property", "mute"]})
        return bool(value)

    @mute.setter
    def mute(self, value):
        self.send_command({"command": ["set_property", "mute", bool(value)]})

    @property
    def keep_open(self):
        return self.send_command({"command": ["get_property", "keep-open"]})

    @keep_open.setter
    def keep_open(self, value):
        self.send_command({"command": ["set_property", "keep-open", "always" if value else "no"]})

    @property
    def keep_open_pause(self):
        return self.send_command({"command": ["get_property", "keep-open-pause"]})

    @keep_open_pause.setter
    def keep_open_pause(self, value):
        self.send_command({"command": ["set_property", "keep-open-pause", bool(value)]})

    @property
    def image_display_duration(self):
        return self._image_display_duration

    @image_display_duration.setter
    def image_display_duration(self, value):
        self._image_display_duration = value

    @property
    def eof_reached(self):
        return self.send_command({"command": ["get_property", "eof-reached"]})

    @property
    def core_idle(self):
        return self.send_command({"command": ["get_property", "core-idle"]})

    @property
    def video_pan_x(self):
        return self.send_command({"command": ["get_property", "video-pan-x"]})

    @video_pan_x.setter
    def video_pan_x(self, value):
        self.send_command({"command": ["set_property", "video-pan-x", value]})

    @property
    def video_pan_y(self):
        return self.send_command({"command": ["get_property", "video-pan-y"]})

    @video_pan_y.setter
    def video_pan_y(self, value):
        self.send_command({"command": ["set_property", "video-pan-y", value]})

    @property
    def hwdec(self):
        return self._hwdec

    @hwdec.setter
    def hwdec(self, value):
        self._hwdec = value

    def create_image_overlay(self, img=None, pos=(0, 0)):
        return _NullOverlay()
