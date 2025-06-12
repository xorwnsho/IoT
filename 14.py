import RPi.GPIO as GPIO
import spidev
import time
import random

# 핀 번호 설정
button_pin = 17
buzzer_pin = 18
led_red_pin = 22
led_green_pin = 23
light_sensor_channel = 0  # 조도센서가 연결된 MCP3208의 채널 번호

# 7-Segment 핀 정의
segment_pins = {
    'A': 4,    # S0
    'B': 5,    # S1
    'C': 6,    # S2
    'D': 12,   # S3
    'E': 13,   # S4
    'F': 19,   # S5
    'DP': 26   # DP
}

# 각 숫자별 Segment 패턴
number_patterns = {
    0: [1,1,1,1,1,1,0],
    1: [0,1,1,0,0,0,0],
    2: [1,1,0,1,1,0,1],
    3: [1,1,1,1,0,0,1],
    4: [0,1,1,0,0,1,1],
    5: [1,0,1,1,0,1,1],
    6: [1,0,1,1,1,1,1],
    7: [1,1,1,0,0,0,0],
    8: [1,1,1,1,1,1,1],
    9: [1,1,1,1,0,1,1]
}

# SPI 설정 (조도센서 읽기용)
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.setup(led_red_pin, GPIO.OUT)
GPIO.setup(led_green_pin, GPIO.OUT)

# 7-Segment 핀을 출력으로 설정
for pin in segment_pins.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# PWM 만들기 (소리, 불빛 조절)
buzzer = GPIO.PWM(buzzer_pin, 1000)
led_red = GPIO.PWM(led_red_pin, 1000)
led_green = GPIO.PWM(led_green_pin, 1000)

# 처음에는 다 끈 상태로 시작
buzzer.start(0)
led_red.start(0)
led_green.start(0)

# 버튼이 눌릴 때까지 기다리는 함수
def wait_for_button():
    while GPIO.input(button_pin) == GPIO.HIGH:
        time.sleep(0.01)
    while GPIO.input(button_pin) == GPIO.LOW:
        time.sleep(0.01)

# 조도센서에서 숫자값을 읽는 함수
def read_light():
    value = spi.xfer2([6 | (light_sensor_channel >> 2), (light_sensor_channel & 3) << 6, 0])
    light_level = ((value[1] & 15) << 8) | value[2]
    return light_level

# 숫자 표시 함수 (정수 한 자리만 표시)
def display_number(n):
    if n < 0 or n > 9:
        print("Number out of range")
        return
    
    pattern = number_patterns[n]
    keys = ['A','B','C','D','E','F','DP']
    for i, key in enumerate(keys):
        GPIO.output(segment_pins[key], GPIO.HIGH if pattern[i] else GPIO.LOW)

# 반응이 느릴 때 불빛과 부저로 경고하기
def blink_led_and_buzzer():
    light = read_light()
    is_dark = light < 300

    print(f"Light level: {light} → {'Dark' if is_dark else 'Bright'}")

    buzzer.ChangeDutyCycle(50)

    for i in range(5):
        if is_dark:
            led_red.ChangeDutyCycle(20)
            led_green.ChangeDutyCycle(0)
        else:
            led_red.ChangeDutyCycle(100)
            led_green.ChangeDutyCycle(0)

        time.sleep(0.3)

        if is_dark:
            led_red.ChangeDutyCycle(0)
            led_green.ChangeDutyCycle(20)
        else:
            led_red.ChangeDutyCycle(0)
            led_green.ChangeDutyCycle(100)

        time.sleep(0.3)

    buzzer.ChangeDutyCycle(0)
    led_red.ChangeDutyCycle(0)
    led_green.ChangeDutyCycle(0)

# 반응 속도 테스트
def start_test():
    print("\n[Reaction Test Started]")
    slow_reaction_count = 0

    for round_number in range(3):
        wait_seconds = random.uniform(1, 5)
        print(f"\nRound {round_number + 1}: Waiting for {wait_seconds:.2f} seconds...")
        time.sleep(wait_seconds)

        print("Buzzer ON! Press the button!")
        buzzer.ChangeDutyCycle(50)
        start_time = time.time()

        wait_for_button()

        end_time = time.time()
        buzzer.ChangeDutyCycle(0)

        reaction_time = end_time - start_time
        print(f"Reaction time: {reaction_time:.3f} seconds")

        # 7-Segment 에 반응속도 초의 첫째자리 표시
        first_digit = int(reaction_time)
        display_number(first_digit)

        if reaction_time > 0.5:
            slow_reaction_count += 1

    print("\n[Result]")
    if slow_reaction_count >= 2:
        print("Too slow! You might be sleepy. Please take a break.")
        blink_led_and_buzzer()
    else:
        print("Good reaction. No sign of sleepiness.")

# 프로그램 시작
try:
    print("Welcome! Press the button to start the reaction test.")

    while True:
        wait_for_button()
        start_test()

except KeyboardInterrupt:
    print("Program stopped by user.")

finally:
    buzzer.stop()
    led_red.stop()
    led_green.stop()
    GPIO.cleanup()
    spi.close()

