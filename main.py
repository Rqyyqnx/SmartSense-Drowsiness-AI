import cv2
import mediapipe as mp
import time
import pygame
import numpy as np

# === Sound Setup ===
pygame.mixer.init()
beep_sound = pygame.mixer.Sound("static/alert.wav")  # For eyes
beep_sound.set_volume(1.0)

head_beep_sound = pygame.mixer.Sound("static/alert_head.wav")  # For head movement
head_beep_sound.set_volume(1.0)

def beep():
    beep_sound.play()

# === Mediapipe Setup ===
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
mp_draw = mp.solutions.drawing_utils

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
LEFT_EYE_CENTER = 159
RIGHT_EYE_CENTER = 386
NOSE_TIP = 1

# === Video Setup ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

last_drowsy_alert = 0
head_tilt_alert_time = 0

EAR_THRESHOLD = 0.18

def eye_aspect_ratio(landmarks, eye):
    p1, p2, p3, p4, p5, p6 = [landmarks[i] for i in eye]
    vertical_1 = ((p2.y - p6.y)**2 + (p2.x - p6.x)**2)**0.5
    vertical_2 = ((p3.y - p5.y)**2 + (p3.x - p5.x)**2)**0.5
    horizontal = ((p1.y - p4.y)**2 + (p1.x - p4.x)**2)**0.5
    return (vertical_1 + vertical_2) / (2.0 * horizontal) if horizontal != 0 else 1

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.resize(img, (1280, 720))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(img_rgb)
    current_time = time.time()
    h, w, _ = img.shape

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmarks = face_landmarks.landmark

            # === DROWSINESS DETECTION (EAR) ===
            left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
            right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
            avg_ear = (left_ear + right_ear) / 2

            if avg_ear < EAR_THRESHOLD:
                if current_time - last_drowsy_alert > 5:
                    cv2.putText(img, "DROWSINESS DETECTED (EAR)", (30, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 255), 3)
                    beep()
                    last_drowsy_alert = current_time

            # === HEAD DIRECTION (DOWN / LEFT / RIGHT) ===
            nose = landmarks[NOSE_TIP]
            left_eye_center = landmarks[LEFT_EYE_CENTER]
            right_eye_center = landmarks[RIGHT_EYE_CENTER]

            nose_y = nose.y * h
            eye_avg_y = ((left_eye_center.y + right_eye_center.y) / 2) * h

            # Looking down
            if nose_y - eye_avg_y > 80:
                cv2.putText(img, "LOOKING DOWN DETECTED", (30, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                if current_time - head_tilt_alert_time > 5:
                    head_beep_sound.play()
                    head_tilt_alert_time = current_time

            # Looking left
            elif nose.x < left_eye_center.x - 0.03:
                cv2.putText(img, "LOOKING LEFT DETECTED", (30, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                if current_time - head_tilt_alert_time > 5:
                    head_beep_sound.play()
                    head_tilt_alert_time = current_time

            # Looking right
            elif nose.x > right_eye_center.x + 0.03:
                cv2.putText(img, "LOOKING RIGHT DETECTED", (30, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                if current_time - head_tilt_alert_time > 5:
                    head_beep_sound.play()
                    head_tilt_alert_time = current_time

            mp_draw.draw_landmarks(img, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS)

    cv2.imshow("SmartSense AI (EAR + Head Direction)", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
