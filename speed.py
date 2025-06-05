import cv2
import time
import board
import adafruit_dht
import RPi.GPIO as GPIO
import random

# ---------- GPIO 설정 ----------
BUTTON_PIN = 17
BUZZER_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# ---------- DHT11 센서 설정 ----------
dhtDevice = adafruit_dht.DHT11(board.D4)  # GPIO 4번 사용

# ---------- 얼굴 인식 모델 ----------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ---------- 반응속도 테스트 ----------
def reaction_test():
    slow_count = 0
    for i in range(3):
        wait_time = random.uniform(2, 5)
        time.sleep(wait_time)

        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        start = time.time()

        # 버튼 대기 (최대 3초)
        timeout = start + 3
        while GPIO.input(BUTTON_PIN) == 0 and time.time() < timeout:
            pass

        GPIO.output(BUZZER_PIN, GPIO.LOW)
        reaction_time = time.time() - start
        print(f"{i+1}번째 반응속도: {reaction_time:.2f}초")

        if reaction_time > 0.5:
            slow_count += 1

    if slow_count >= 2:
        print("⚠️ 반응속도가 느립니다. 휴식이 필요합니다.")

# ---------- 온도 측정 ----------
def check_temperature():
    try:
        temperature_c = dhtDevice.temperature
        print(f"🌡️ 현재 온도: {temperature_c}도")

        if temperature_c < 21 or temperature_c > 23:
            print(f"🔥 차의 온도가 너무 높습니다. {temperature_c}도로 맞춰주세요.")
        else:
            print("✅ 차량 온도 적정 범위입니다.")
    except RuntimeError as error:
        print("DHT11 센서 오류 (무시 가능):", error.args[0])

# ---------- 메인 루프 ----------
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
            print("😊 얼굴이 감지되었습니다.")
        else:
            print("❌ 얼굴이 없습니다.")
            if time.time() - last_seen > 3:
                print("⏱️ 반응속도 테스트 시작!")
                reaction_test()
                last_seen = time.time()

        check_temperature()
        time.sleep(5)

except KeyboardInterrupt:
    print("종료합니다.")
finally:
    cap.release()
    GPIO.cleanup()
