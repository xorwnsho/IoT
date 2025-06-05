import cv2
import time
import RPi.GPIO as GPIO
import random

# ---------- GPIO Setup ----------
BUTTON_PIN = 17
BUZZER_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# ---------- Load Haar Cascade (Make sure this file is in the same folder) ----------
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# ---------- Reaction Time Test ----------
def reaction_test():
    slow_count = 0
    for i in range(3):
        wait_time = random.uniform(2, 5)
        time.sleep(wait_time)

        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        start = time.time()

        timeout = start + 3
        while GPIO.input(BUTTON_PIN) == 0 and time.time() < timeout:
            pass

        GPIO.output(BUZZER_PIN, GPIO.LOW)
        reaction_time = time.time() - start
        print(f"Test {i+1} - Reaction Time: {reaction_time:.2f} seconds")

        if reaction_time > 0.5:
            slow_count += 1

    if slow_count >= 2:
        print("⚠️ Your reaction is slow. You may need to take a break.")

# ---------- Main Loop ----------
cap = cv2.VideoCapture(0)
last_seen = time.time()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            last_seen = time.time()
            print("😊 Face detected.")
        else:
            print("❌ No face detected.")
            if time.time() - last_seen > 3:
                print("⏱️ Starting reaction time test!")
                reaction_test()
                last_seen = time.time()

        time.sleep(5)

except KeyboardInterrupt:
    print("Program terminated.")
finally:
    cap.release()
    GPIO.cleanup()
