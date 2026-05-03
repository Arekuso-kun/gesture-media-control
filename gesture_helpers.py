import math

from gesture_constants import MCP_IDS, PINCH_TOUCH_RATIO, PIP_IDS, TIP_IDS


def landmark_distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def get_hand_scale(landmarks):
    palm_width = landmark_distance(landmarks[5], landmarks[17])
    palm_height = landmark_distance(landmarks[0], landmarks[9])
    return (palm_width + palm_height) / 2


def is_thumb_extended(landmarks):
    return abs(landmarks[4].x - landmarks[5].x) > 0.10


def is_finger_up(landmarks, finger_name):
    tip_id = TIP_IDS[finger_name]
    pip_id = PIP_IDS[finger_name]
    mcp_id = MCP_IDS[finger_name]
    wrist = landmarks[0]

    tip_to_mcp = landmark_distance(landmarks[tip_id], landmarks[mcp_id])
    pip_to_mcp = landmark_distance(landmarks[pip_id], landmarks[mcp_id])
    tip_to_wrist = landmark_distance(landmarks[tip_id], wrist)
    pip_to_wrist = landmark_distance(landmarks[pip_id], wrist)

    return tip_to_mcp > pip_to_mcp * 1.35 and tip_to_wrist > pip_to_wrist * 1.1


def is_thumb_pointing_horizontal(landmarks, direction):
    if not is_thumb_extended(landmarks):
        return False
    if direction == "right":
        return landmarks[4].x > landmarks[3].x > landmarks[2].x
    return landmarks[4].x < landmarks[3].x < landmarks[2].x


def is_thumb_furthest_horizontal(landmarks, direction, margin=0.02):
    thumb_tip_x = landmarks[4].x
    other_x_values = [point.x for index, point in enumerate(landmarks) if index != 4]

    if not is_thumb_extended(landmarks):
        return False
    if direction == "right":
        return thumb_tip_x > max(other_x_values) + margin
    return thumb_tip_x < min(other_x_values) - margin


def is_index_pointing_vertical(landmarks, direction):
    if direction == "down":
        return landmarks[8].y > landmarks[7].y > landmarks[6].y
    return landmarks[8].y < landmarks[7].y < landmarks[6].y


def is_index_furthest_vertical(landmarks, direction, margin=0.02):
    index_tip_y = landmarks[8].y
    other_y_values = [point.y for index, point in enumerate(landmarks) if index != 8]
    if direction == "down":
        return index_tip_y > max(other_y_values) + margin
    return index_tip_y < min(other_y_values) - margin


def is_thumb_index_touching(landmarks):
    thumb_index_distance = landmark_distance(landmarks[4], landmarks[8])
    hand_scale = get_hand_scale(landmarks)
    return thumb_index_distance < hand_scale * PINCH_TOUCH_RATIO


def get_four_finger_tilt_degrees(landmarks):
    finger_names = ("index", "middle", "ring", "pinky")
    angles = []

    for finger_name in finger_names:
        tip = landmarks[TIP_IDS[finger_name]]
        mcp = landmarks[MCP_IDS[finger_name]]
        dx = tip.x - mcp.x
        dy = tip.y - mcp.y
        angle = math.degrees(math.atan2(-dy, abs(dx) + 1e-6))
        angles.append(angle)

    return sum(angles) / len(angles)


def get_finger_states(hand_landmarks):
    lm = hand_landmarks.landmark
    return {
        "thumb": is_thumb_extended(lm),
        "index": is_finger_up(lm, "index"),
        "middle": is_finger_up(lm, "middle"),
        "ring": is_finger_up(lm, "ring"),
        "pinky": is_finger_up(lm, "pinky"),
    }
