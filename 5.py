import RPi.GPIO as GPIO
import time
import random

# GPIO setup
BUTTON_PIN = 17
BUZZER_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

reaction_times = []

def wait_for_button_press():
    while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
        time.sleep(0.01)
    while GPIO.input(BUTTON_PIN) == GPIO.LOW:
        time.sleep(0.01)

def run_test():
    print("Start the drowsy driving test.")
    reaction_times.clear()
    slow_reactions = 0
    
    for i in range(3):
        wait_time = random.uniform(1, 5)
        print(f"\nRound {i+1}: Wait for {wait_time:.2f} seconds...")
        
        time.sleep(wait_time)
        
        print("Buzzer ON! React now!")
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        start_time = time.time()
        
        wait_for_button_press()
        
        end_time = time.time()
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        
        reaction_time = end_time - start_time
        reaction_times.append(reaction_time)
        
        print(f"Your reaction time: {reaction_time:.3f} seconds")
        
        if reaction_time > 0.5:
            slow_reactions += 1
    
    # Evaluation
    print("\nTest Result:")
    if slow_reactions >= 2:
        print("Drowsy driving is suspected. Take a break.")
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
    GPIO.cleanup()

