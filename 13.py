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
    G

