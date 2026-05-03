from gesture_constants import (
    DYNAMIC_VOLUME_DEADZONE_DEGREES,
    DYNAMIC_VOLUME_MAX_STEPS,
    DYNAMIC_VOLUME_STEP_DEGREES,
)
from gesture_helpers import (
    get_four_finger_tilt_degrees,
    get_finger_states,
    is_index_furthest_vertical,
    is_index_pointing_vertical,
    is_thumb_furthest_horizontal,
    is_thumb_pointing_horizontal,
)


def detect_gesture(hand_landmarks):
    lm = hand_landmarks.landmark
    finger_states = get_finger_states(hand_landmarks)

    thumb_extended = finger_states["thumb"]
    index_up = finger_states["index"]
    middle_up = finger_states["middle"]
    ring_up = finger_states["ring"]
    pinky_up = finger_states["pinky"]

    index_pointing_up = is_index_pointing_vertical(lm, "up")
    index_pointing_down = is_index_pointing_vertical(lm, "down")
    index_furthest_up = is_index_furthest_vertical(lm, "up")
    index_furthest_down = is_index_furthest_vertical(lm, "down")
    index_up_gesture = index_pointing_up and index_furthest_up
    index_down_gesture = index_pointing_down and index_furthest_down

    thumb_pointing_right = is_thumb_pointing_horizontal(lm, "right")
    thumb_pointing_left = is_thumb_pointing_horizontal(lm, "left")
    thumb_furthest_right = is_thumb_furthest_horizontal(lm, "right")
    thumb_furthest_left = is_thumb_furthest_horizontal(lm, "left")
    thumb_right_gesture = thumb_pointing_right and thumb_furthest_right
    thumb_left_gesture = thumb_pointing_left and thumb_furthest_left

    other_fingers_up = [index_up, middle_up, ring_up, pinky_up]
    all_other_up = all(other_fingers_up)
    all_other_down = not any(other_fingers_up)

    thumb_horizontal_dominant = thumb_right_gesture or thumb_left_gesture

    if all_other_up and thumb_extended:
        return "PALM_OPEN"

    if all_other_down and thumb_right_gesture:
        return "THUMB_RIGHT"

    if all_other_down and thumb_left_gesture:
        return "THUMB_LEFT"

    if index_up and middle_up and not ring_up and not pinky_up:
        return "TWO_FINGERS"

    if (
        index_up_gesture
        and not thumb_horizontal_dominant
        and not middle_up
        and not ring_up
        and not pinky_up
    ):
        return "INDEX_UP"

    if (
        index_down_gesture
        and not thumb_horizontal_dominant
        and not middle_up
        and not ring_up
        and not pinky_up
    ):
        return "INDEX_DOWN"
    return "NONE"


def detect_dynamic_volume_gesture(hand_landmarks):
    lm = hand_landmarks.landmark
    finger_states = get_finger_states(hand_landmarks)
    thumb_extended = finger_states["thumb"]
    four_fingers_extended = all(
        finger_states[finger_name]
        for finger_name in ("index", "middle", "ring", "pinky")
    )

    if not four_fingers_extended or thumb_extended:
        return None

    angle_degrees = get_four_finger_tilt_degrees(lm)
    abs_angle = abs(angle_degrees)

    if abs_angle < DYNAMIC_VOLUME_DEADZONE_DEGREES:
        return {
            "gesture": "NONE",
            "steps": 0,
            "angle_degrees": angle_degrees,
        }

    steps = 1 + int(
        (abs_angle - DYNAMIC_VOLUME_DEADZONE_DEGREES) / DYNAMIC_VOLUME_STEP_DEGREES
    )
    steps = min(steps, DYNAMIC_VOLUME_MAX_STEPS)

    if angle_degrees > 0:
        gesture = "FOUR_FINGERS_VOLUME_UP"
    else:
        gesture = "FOUR_FINGERS_VOLUME_DOWN"

    return {
        "gesture": gesture,
        "steps": steps,
        "angle_degrees": angle_degrees,
    }


def detect_post_pinch_fullscreen_pose(hand_landmarks):
    lm = hand_landmarks.landmark
    index_furthest_up = is_index_furthest_vertical(lm, "up")
    thumb_furthest_side = is_thumb_furthest_horizontal(
        lm, "left"
    ) or is_thumb_furthest_horizontal(lm, "right")

    return index_furthest_up and thumb_furthest_side
