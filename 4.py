import cv2
import time
import RPi.GPIO as GPIO
import random

# GPIO setup
BUTTON_PIN = 17
BUZZER_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Load Haar Cascade (same directory)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def reaction_test():
    slow_count = 0
    for i in range(3):
        wait_time = random.uniform(2, 4)
        time.sleep(wait_time)

        print(f"🔊 Test {i+1} - Buzzer ON")
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        start_time = time.time()
        pressed = False

        while time.time() - start_time < 3:
            if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
                pressed = True
                break

        GPIO.output(BUZZER_PIN, GPIO.LOW)

        if pressed:
            reaction_time = time.time() - start_time
            print(f"✅ Reaction Time: {reaction_time:.2f} seconds")
            if reaction_time > 0.5:
                slow_count += 1
        else:
            print(f"❌ No button press. Reaction too slow.")
            slow_count += 1

    if slow_count >= 2:
        print("⚠️ Your reaction is slow. You may need to take a break.")

# Main loop
cap = cv2.VideoCapture(0)  # Try 0 or 1 if camera not found
if not cap.isOpened():
    print("❌ Camera not detected. Check connection or use libcamera.")
    exit()

last_seen = time.time()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame from camera.")
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
    print("Program stopped.")
finally:
    cap.release()
    GPIO.cleanup()
