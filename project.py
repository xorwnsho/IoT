import cv2
import time
from gpiozero import Button, Buzzer
from signal import pause

# 얼굴 인식용 Haar Cascade 로드
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 부저와 버튼 설정
buzzer = Buzzer(18)   # GPIO 18
button = Button(17)   # GPIO 17

def face_detected(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return len(faces) > 0

def reaction_test():
    fail_count = 0
    for i in range(3):
        time.sleep(1)  # 짧은 대기
        buzzer.on()
        time.sleep(0.2)
        buzzer.off()
        
        start_time = time.time()
        button.wait_for_press(timeout=5)  # 버튼을 누를 때까지 대기 (최대 5초)
        reaction_time = time.time() - start_time
        
        print(f"Reaction {i+1}: {reaction_time:.2f} sec")
        
        if reaction_time > 0.5:
            fail_count += 1

    if fail_count >= 2:
        print("You need a rest")

def main():
    cap = cv2.VideoCapture(0)  # Camera Module 2 사용

    print("Starting camera. Press Ctrl+C to stop.")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            if face_detected(frame):
                continue  # 얼굴이 있으면 계속 모니터링

            # 얼굴이 없을 경우 1초 대기
            time.sleep(1)

            # 1초 뒤 다시 확인
            ret, frame = cap.read()
            if not face_detected(frame):
                print("No face detected. Starting reaction test...")
                reaction_test()

    except KeyboardInterrupt:
        print("Program stopped.")
    finally:
        cap.release()

if __name__ == "__main__":
    main()

