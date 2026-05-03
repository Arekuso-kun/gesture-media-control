import time

import cv2
import mediapipe as mp

from gesture_actions import execute_action
from gesture_constants import (
    COMMAND_COOLDOWN,
    COMMAND_HOLD_TIME,
    PINCH_ARM_TIMEOUT,
    VOLUME_COOLDOWN,
    VOLUME_REPEAT_DELAY,
    VOLUME_HOLD_TIME,
)
from gesture_detection import (
    detect_dynamic_volume_gesture,
    detect_gesture,
    detect_post_pinch_fullscreen_pose,
)
from gesture_helpers import (
    get_finger_states,
    is_thumb_index_touching,
)

VOLUME_GESTURES = {
    "INDEX_UP",
    "INDEX_DOWN",
    "FOUR_FINGERS_VOLUME_UP",
    "FOUR_FINGERS_VOLUME_DOWN",
}

GESTURE_LABELS = {
    "NONE": "No Gesture",
    "PALM_OPEN": "Open Palm",
    "THUMB_RIGHT": "Thumb Right",
    "THUMB_LEFT": "Thumb Left",
    "INDEX_UP": "Index Up",
    "INDEX_DOWN": "Index Down",
    "FOUR_FINGERS_VOLUME_UP": "Dynamic Volume Up",
    "FOUR_FINGERS_VOLUME_DOWN": "Dynamic Volume Down",
    "PINCH_ZOOM_IN": "Pinch Fullscreen",
    "TWO_FINGERS": "Two Fingers",
}


def format_gesture_label(gesture):
    return GESTURE_LABELS.get(gesture, gesture)


def main():
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open the webcam.")
        return

    last_command_time = 0
    last_volume_time = 0
    current_gesture = "NONE"
    previous_gesture = "NONE"
    tracked_gesture = "NONE"
    tracked_gesture_since = time.time()
    last_action_text = "No Action"
    finger_detail_text = "Fingers: T:0 I:0 M:0 R:0 P:0"
    pinch_status_text = "Pinch: idle"
    pinch_armed = False
    pinch_armed_since = 0.0
    active_volume_gesture = "NONE"
    active_volume_since = 0.0
    volume_initial_triggered = False
    current_volume_repeat_count = 1
    volume_status_text = "Dynamic Volume: idle"

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    ) as hands:
        while True:
            success, frame = cap.read()
            if not success:
                print("Cannot read a frame from the webcam.")
                break

            frame = cv2.flip(frame, 1)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            current_gesture = "NONE"

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]

                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                )

                finger_states = get_finger_states(hand_landmarks)
                finger_detail_text = (
                    f"Fingers: T:{int(finger_states['thumb'])} "
                    f"I:{int(finger_states['index'])} "
                    f"M:{int(finger_states['middle'])} "
                    f"R:{int(finger_states['ring'])} "
                    f"P:{int(finger_states['pinky'])}"
                )

                current_gesture = detect_gesture(hand_landmarks)
                current_volume_repeat_count = 1
                dynamic_volume = detect_dynamic_volume_gesture(hand_landmarks)
                if dynamic_volume is not None:
                    angle_degrees = dynamic_volume["angle_degrees"]
                    if dynamic_volume["gesture"] == "NONE":
                        volume_status_text = (
                            f"Dynamic Volume: neutral {angle_degrees:.0f} deg"
                        )
                    else:
                        current_gesture = dynamic_volume["gesture"]
                        current_volume_repeat_count = dynamic_volume["steps"]
                        volume_status_text = (
                            f"Dynamic Volume: {angle_degrees:.0f} deg "
                            f"x{current_volume_repeat_count}"
                        )
                else:
                    volume_status_text = "Dynamic Volume: idle"

                pinching = is_thumb_index_touching(hand_landmarks.landmark)

                if pinching:
                    pinch_armed = True
                    pinch_armed_since = time.time()
                    pinch_status_text = "Pinch: touch"
                    current_gesture = "NONE"
                elif pinch_armed:
                    pinch_status_text = "Pinch: armed"
                    if detect_post_pinch_fullscreen_pose(hand_landmarks):
                        pinch_status_text = "Pinch: fullscreen pose"
                        current_gesture = "PINCH_ZOOM_IN"
                    elif time.time() - pinch_armed_since > PINCH_ARM_TIMEOUT:
                        pinch_armed = False
                        pinch_status_text = "Pinch: idle"
                else:
                    pinch_status_text = "Pinch: idle"

                now = time.time()
                if current_gesture != tracked_gesture:
                    tracked_gesture = current_gesture
                    tracked_gesture_since = now

                if current_gesture in VOLUME_GESTURES:
                    if current_gesture != active_volume_gesture:
                        active_volume_gesture = current_gesture
                        active_volume_since = now
                        volume_initial_triggered = False
                else:
                    active_volume_gesture = "NONE"
                    active_volume_since = 0.0
                    volume_initial_triggered = False

                cooldown = VOLUME_COOLDOWN
                hold_time = VOLUME_HOLD_TIME
                if current_gesture not in VOLUME_GESTURES:
                    cooldown = COMMAND_COOLDOWN
                    hold_time = COMMAND_HOLD_TIME

                held_long_enough = (
                    current_gesture != "NONE"
                    and now - tracked_gesture_since >= hold_time
                )

                should_execute = False
                if current_gesture in VOLUME_GESTURES:
                    if not volume_initial_triggered:
                        should_execute = held_long_enough
                    else:
                        should_execute = (
                            now - active_volume_since >= VOLUME_REPEAT_DELAY
                            and now - last_volume_time > cooldown
                        )
                else:
                    should_execute = (
                        held_long_enough
                        and current_gesture != previous_gesture
                        and now - last_command_time > cooldown
                    )

                if should_execute:
                    last_action_text = execute_action(
                        current_gesture,
                        repeat_count=current_volume_repeat_count,
                    )
                    if current_gesture in VOLUME_GESTURES:
                        last_volume_time = now
                        volume_initial_triggered = True
                    else:
                        last_command_time = now
                        previous_gesture = current_gesture
                        if current_gesture == "PINCH_ZOOM_IN":
                            pinch_armed = False
                            pinch_status_text = "Pinch: idle"
            else:
                finger_detail_text = "Fingers: T:0 I:0 M:0 R:0 P:0"
                pinch_status_text = "Pinch: idle"
                pinch_armed = False
                pinch_armed_since = 0.0
                active_volume_gesture = "NONE"
                active_volume_since = 0.0
                volume_initial_triggered = False
                volume_status_text = "Dynamic Volume: idle"
                tracked_gesture = "NONE"
                tracked_gesture_since = time.time()

            if current_gesture == "NONE":
                previous_gesture = "NONE"

            cv2.putText(
                frame,
                f"Detected Gesture: {format_gesture_label(current_gesture)}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            cv2.putText(
                frame,
                f"Last Action: {last_action_text}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                finger_detail_text,
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 220, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Gesture Hold: {max(0.0, time.time() - tracked_gesture_since):.2f}s",
                (10, 115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (180, 255, 120),
                2,
            )

            cv2.putText(
                frame,
                pinch_status_text,
                (10, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 170, 120),
                2,
            )

            cv2.putText(
                frame,
                volume_status_text,
                (10, 165),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (160, 210, 255),
                2,
            )

            cv2.imshow("Gesture Media Control", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()
