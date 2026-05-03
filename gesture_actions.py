import pyautogui

from gesture_constants import USE_PYAUTOGUI


def execute_action(gesture, repeat_count=1):
    """
    Translate a gesture into a media command.
    If PyAutoGUI is disabled or unavailable, just return the action text.
    """
    if gesture == "PALM_OPEN":
        action_text = "Play / Pause"
        key_name = "playpause"
    elif gesture == "THUMB_RIGHT":
        action_text = "Next"
        key_name = "nexttrack"
    elif gesture == "THUMB_LEFT":
        action_text = "Previous"
        key_name = "prevtrack"
    elif gesture == "INDEX_UP":
        action_text = "Volume +"
        key_name = "volumeup"
    elif gesture == "INDEX_DOWN":
        action_text = "Volume -"
        key_name = "volumedown"
    elif gesture == "FOUR_FINGERS_VOLUME_UP":
        action_text = "Volume +"
        key_name = "volumeup"
    elif gesture == "FOUR_FINGERS_VOLUME_DOWN":
        action_text = "Volume -"
        key_name = "volumedown"
    elif gesture == "PINCH_ZOOM_IN":
        action_text = "Fullscreen"
        key_name = "f11"
    elif gesture == "TWO_FINGERS":
        action_text = "Mute"
        key_name = "volumemute"
    else:
        return ""

    if USE_PYAUTOGUI:
        for _ in range(repeat_count):
            pyautogui.press(key_name)

    print(
        f"[COMMAND] gesture={gesture} action={action_text} repeat_count={repeat_count}"
    )
    return action_text
