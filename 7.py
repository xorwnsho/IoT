import RPi.GPIO as GPIO
import time
import random

# GPIO setup
BUTTON_PIN = 17
BUZZER_PIN = 18
LED1_PIN = 22
LED2_PIN = 23
LIGHT_SENSOR_PIN = 24  # 포토레지스터 디지털 입력

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(LED1_PIN, GPIO.OUT)
GPIO.setup(LED2_PIN, GPIO.OUT)
GPIO.setup(LIGHT_SENSOR_PIN, GPIO.IN)  # 조도센서 디지털 입력으로 가정

# PWM 객체 생성
pwm = GPIO.PWM(BUZZER_PIN, 1000)  # 1kHz tone

reaction_times = []

def wait_for_button_press():
    while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
        time.sleep(0.01)
    while GPIO.input(BUTTON_PIN) == GPIO.LOW:
        time.sleep(0.01)

def blink_leds_with_buzzer():
    is_night = GPIO.input(LIGHT_SENSOR_PIN) == GPIO.LOW  # LOW면 밤
    
    print("Night mode." if is_night else "Day mode.")

    pwm.start(50)  # Buzzer ON
    
    start_time = time.time()
    while (time.time() - start_time) < 5:  # 5초 동안 반복
        # LED1 ON, LED2 OFF
        GPIO.output(LED1_PIN, GPIO.HIGH if not is_night else GPIO.LOW)  # 밤이면 LED 밝기 낮추는 효과
        GPIO.output(LED2_PIN, GPIO.LOW)
        time.sleep(0.3)
        
        # LED1 OFF, LED2 ON
        GPIO.output(LED1_PIN, GPIO.LOW)
        GPIO.output(LED2_PIN, GPIO.HIGH if not is_night else GPIO.LOW)
        time.sleep(0.3)
    
    # 모두 OFF
    GPIO.output(LED1_PIN, GPIO.LOW)
    GPIO.output(LED2_PIN, GPIO.LOW)
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
    print("Press the button to start the drowsy driving test.")
    while True:
        wait_for_button_press()
        run_test()

except KeyboardInterrupt:
    print("Exiting program.")

finally:
    pwm.stop()
    GPIO.cleanup()

