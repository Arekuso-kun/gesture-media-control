import ctypes
from pathlib import Path

import pyautogui

try:
    from pycaw.pycaw import AudioUtilities
except ImportError:
    AudioUtilities = None

from gesture_constants import (
    APP_VOLUME_STEP,
    DEFAULT_APP_VOLUME_DOWN_BINDING,
    DEFAULT_APP_VOLUME_UP_BINDING,
    DEFAULT_FULLSCREEN_BINDING,
    USE_PYAUTOGUI,
)

BROWSER_PROCESS_NAMES = {
    "brave.exe",
    "chrome.exe",
    "firefox.exe",
    "msedge.exe",
    "opera.exe",
}

PLAYER_FULLSCREEN_PROCESSES = {
    "vlc.exe",
}


def trigger_key_binding(key_binding):
    if isinstance(key_binding, (tuple, list)):
        pyautogui.hotkey(*key_binding)
        return

    pyautogui.press(key_binding)


def get_window_text(hwnd):
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""

    buffer = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def get_process_name(pid):
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    process_handle = ctypes.windll.kernel32.OpenProcess(
        PROCESS_QUERY_LIMITED_INFORMATION,
        False,
        pid,
    )
    if not process_handle:
        return ""

    try:
        buffer_length = ctypes.c_ulong(260)
        buffer = ctypes.create_unicode_buffer(buffer_length.value)
        success = ctypes.windll.kernel32.QueryFullProcessImageNameW(
            process_handle,
            0,
            buffer,
            ctypes.byref(buffer_length),
        )
        if not success:
            return ""

        return Path(buffer.value).name.lower()
    finally:
        ctypes.windll.kernel32.CloseHandle(process_handle)


def get_foreground_window_context():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    if not hwnd:
        return {
            "pid": 0,
            "process_name": "",
            "title": "",
        }

    process_id = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
    return {
        "pid": process_id.value,
        "process_name": get_process_name(process_id.value),
        "title": get_window_text(hwnd).lower(),
    }


def get_matching_audio_sessions(pid, process_name):
    if AudioUtilities is None:
        return []

    exact_pid_sessions = []
    same_process_sessions = []

    for session in AudioUtilities.GetAllSessions():
        process = session.Process
        if process is None:
            continue

        session_pid = getattr(process, "pid", None)
        session_name = ""
        try:
            session_name = Path(process.exe()).name.lower()
        except Exception:
            session_name = ""

        if session_pid == pid:
            exact_pid_sessions.append(session)
        elif process_name and session_name == process_name:
            same_process_sessions.append(session)

    if exact_pid_sessions:
        return exact_pid_sessions

    return same_process_sessions


def adjust_app_volume(direction, repeat_count):
    context = get_foreground_window_context()
    pid = context["pid"]
    process_name = context["process_name"]
    if not pid or not process_name:
        return False

    sessions = get_matching_audio_sessions(pid, process_name)
    if not sessions:
        return False

    delta = APP_VOLUME_STEP * max(1, repeat_count)
    if direction < 0:
        delta *= -1

    for session in sessions:
        volume = session.SimpleAudioVolume
        current_volume = volume.GetMasterVolume()
        new_volume = min(1.0, max(0.0, current_volume + delta))
        volume.SetMasterVolume(new_volume, None)

    return True


def get_fullscreen_binding():
    context = get_foreground_window_context()
    process_name = context["process_name"]
    title = context["title"]

    if process_name in PLAYER_FULLSCREEN_PROCESSES:
        return "Player Fullscreen", "f"

    if process_name in BROWSER_PROCESS_NAMES and "youtube" in title:
        return "YouTube Fullscreen", "f"

    return "Fullscreen", DEFAULT_FULLSCREEN_BINDING


def execute_action(gesture, repeat_count=1):
    """
    Translate a gesture into a media command.
    If PyAutoGUI is disabled or unavailable, just return the action text.
    """
    if gesture == "PALM_OPEN":
        action_text = "Play / Pause"
        key_binding = "playpause"
    elif gesture == "THUMB_RIGHT":
        action_text = "Next"
        key_binding = "nexttrack"
    elif gesture == "THUMB_LEFT":
        action_text = "Previous"
        key_binding = "prevtrack"
    elif gesture == "INDEX_UP":
        action_text = "Volume +"
        key_binding = "volumeup"
    elif gesture == "INDEX_DOWN":
        action_text = "Volume -"
        key_binding = "volumedown"
    elif gesture == "FOUR_FINGERS_VOLUME_UP":
        action_text = "App Volume +"
        if USE_PYAUTOGUI and adjust_app_volume(1, repeat_count):
            print(
                f"[COMMAND] gesture={gesture} action={action_text} repeat_count={repeat_count}"
            )
            return action_text
        key_binding = DEFAULT_APP_VOLUME_UP_BINDING
    elif gesture == "FOUR_FINGERS_VOLUME_DOWN":
        action_text = "App Volume -"
        if USE_PYAUTOGUI and adjust_app_volume(-1, repeat_count):
            print(
                f"[COMMAND] gesture={gesture} action={action_text} repeat_count={repeat_count}"
            )
            return action_text
        key_binding = DEFAULT_APP_VOLUME_DOWN_BINDING
    elif gesture == "PINCH_ZOOM_IN":
        action_text, key_binding = get_fullscreen_binding()
    elif gesture == "TWO_FINGERS":
        action_text = "Mute"
        key_binding = "volumemute"
    else:
        return ""

    if USE_PYAUTOGUI:
        for _ in range(repeat_count):
            trigger_key_binding(key_binding)

    print(
        f"[COMMAND] gesture={gesture} action={action_text} repeat_count={repeat_count}"
    )
    return action_text
