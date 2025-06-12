import RPi.GPIO as GPIO
import spidev
import Adafruit_DHT
import threading
import time
import random

# SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, device 0
spi.max_speed_hz = 1000000  # SPI_SPEED

# GPIO setup
BUTTON_PIN = 17
BUZZER_PIN = 18
LED1_PIN = 22
LED2_PIN = 23
DHT_PIN = 4  # 온습도 센서 DHT DATA 핀 → GPIO4 사용

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(LED1_PIN, GPIO.OUT)
GPIO.setup(LED2_PIN, GPIO.OUT)

# PWM 객체 생성
pwm = GPIO.PWM(BUZZER_PIN, 1000)  # 1kHz tone
led1_pwm = GPIO.PWM(LED1_PIN, 1000)  # LED PWM 1kHz
led2_pwm = GPIO.PWM(LED2_PIN, 1000)

# PWM start (초기 duty 0)
led1_pwm.start(0)
led2_pwm.start(0)

reaction_times = []

# 온도 측정 쓰레드 종료 flag
stop_temp_thread = False

def read_adc(channel):
    # MCP3208 SPI 읽기
    adc = spi.xfer2([6 | (channel >> 2), (channel & 3) << 6, 0])
    data = ((adc[1] & 15) << 8) | adc[2]
    return data

def read_temperature():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_PIN)
    return temperature

def temperature_monitor():
    while not stop_temp_thread:
        temp = read_temperature()
        if temp is not None:
            print(f"\nCurrent temperature: {temp:.1f}°C")
            if temp <= 21:
                print("Increase the temperature")
            elif temp >= 23:
                print("Decrease the temperature")
            else:
                print("Temperature is optimal")
        else:
            print("Failed to read temperature data")
        
        # 3분 대기
        time.sleep(180)

def wait_for_button_press():
    while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
        time.sleep(0.01)
    while GPIO.input(BUTTON_PIN) == GPIO.LOW:
        time.sleep(0.01)

def blink_leds_with_buzzer():
    light_value = read_adc(0)  # MCP3208 CH0에서 조도센서 값 읽기
    is_night = light_value < 300  # 300 이하이면 밤으로 판단 (기준값은 조도센서에 따라 조절 가능)

    print(f"Light value: {light_value}, {'Night mode' if is_night else 'Day mode'}")

    pwm.start(50)  # Buzzer ON
    
    start_time = time.time()
    while (time.time() - start_time) < 5:  # 5초 동안 반복
        # LED1 ON, LED2 OFF
        if is_night:
            led1_pwm.ChangeDutyCycle(20)  # 밤: 20% 밝기
            led2_pwm.ChangeDutyCycle(0)
        else:
            led1_pwm.ChangeDutyCycle(100)  # 낮: 100% 밝기
            led2_pwm.ChangeDutyCycle(0)

        time.sleep(0.3)

        # LED1 OFF, LED2 ON
        if is_night:
            led1_pwm.ChangeDutyCycle(0)
            led2_pwm.ChangeDutyCycle(20)
        else:
            led1_pwm.ChangeDutyCycle(0)
            led2_pwm.ChangeDutyCycle(100)

        time.sleep(0.3)
    
    # 모두 OFF
    led1_pwm.ChangeDutyCycle(0)
    led2_pwm.ChangeDutyCycle(0)
    pwm.stop()  # Buzzer OFF

def run_test():
    print("Start the drowsy driving test.")
    reaction_times.clear()
    slow_reactions = 0
    
    for i in range(3):
        wait_time = random.uniform(1, 5)
        print(f"\nRound {i+1}: Wait for {wait_time:.2f} seconds...")
        
        time.sleep(wait_time)
        
        print("Buzzer ON! React now!")
        pwm.start(50)  # Buzzer ON (50% duty cycle)
        start_time = time.time()
        
        wait_for_button_press()
        
        end_time = time.time()
        pwm.stop()  # Buzzer OFF
        
        reaction_time = end_time - start_time
        reaction_times.append(reaction_time)
        
        print(f"Your reaction time: {reaction_time:.3f} seconds")
        
        if reaction_time > 0.5:
            slow_reactions += 1
    
    # Evaluation
    print("\nTest Result:")
    if slow_reactions >= 2:
        print("Drowsy driving is suspected. Take a break.")
        blink_leds_with_buzzer()  # 추가된 부분
    else:
        print("It's not drowsy driving yet.")

# Main loop
try:
    # 온도 모니터링 쓰레드 시작
    temp_thread = threading.Thread(target=temperature_monitor)
    temp_thread.start()

    print("Press the button to start the drowsy driving test.")
    while True:
        wait_for_button_press()
        run_test()

except KeyboardInterrupt:
    print("Exiting program.")

finally:
    global stop_temp_thread
    stop_temp_thread = True  # 쓰레드 종료 요청
    temp_thread.join()  # 쓰레드 종료 대기
    
    pwm.stop()
    led1_pwm.stop()
    led2_pwm.stop()
    GPIO.cleanup()
    spi.close()

