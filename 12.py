import RPi.GPIO as GPIO
import spidev
import time
import random
from RPLCD.gpio import CharLCD

# SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, device 0
spi.max_speed_hz = 1000000  # SPI_SPEED

# GPIO setup
BUTTON_PIN = 17
BUZZER_PIN = 18
LED1_PIN = 22
LED2_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(LED1_PIN, GPIO.OUT)
GPIO.setup(LED2_PIN, GPIO.OUT)

# LCD setup
lcd = CharLCD(cols=16, rows=2,
              pin_rs=5, pin_e=6,
              pins_data=[12, 13, 19, 26],
              numbering_mode=GPIO.BCM)

# PWM 객체 생성
pwm = GPIO.PWM(BUZZER_PIN, 1000)  # 1kHz tone
led1_pwm = GPIO.PWM(LED1_PIN, 1000)  # LED PWM 1kHz
led2_pwm = GPIO.PWM(LED2_PIN, 1000)

# PWM start (초기 duty 0)
led1_pwm.start(0)
led2_pwm.start(0)

reaction_times = []

def wait_for_button_press():
    while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
        time.sleep(0.01)
    while GPIO.input(BUTTON_PIN) == GPIO.LOW:
        time.sleep(0.01)

def read_adc(channel):
    # MCP3208 SPI 읽기
    adc = spi.xfer2([6 | (channel >> 2), (channel & 3) << 6, 0])
    data = ((adc[1] & 15) << 8) | adc[2]
    return data

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
        print(f"\nRound {i+1}")
        
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
        
        # LCD 출력 추가
        lcd.clear()
        lcd.write_string("Drowsy driving!")
        lcd.cursor_pos = (1, 0)
        lcd.write_string("Take a break.")
        
        blink_leds_with_buzzer()
    else:
        print("It's not drowsy driving yet.")
        
        # LCD 출력 추가
        lcd.clear()
        lcd.write_string("Driving normal.")
        lcd.cursor_pos = (1, 0)
        lcd.write_string("Be safe!")

# Main loop
try:
    print("Press the button to start the drowsy driving test.")
    lcd.clear()
    lcd.write_string("Press button to")
    lcd.cursor_pos = (1, 0)
    lcd.write_string("start test.")

    while True:
        wait_for_button_press()
        run_test()

except KeyboardInterrupt:
    print("Exiting program.")

finally:
    pwm.stop()
    led1_pwm.stop()
    led2_pwm.stop()
    GPIO.cleanup()
    spi.close()

