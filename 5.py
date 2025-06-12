import time
import random
from gpiozero import Button, Buzzer
from signal import pause

# GPIO Pin Setup
start_button = Button(17)  # GPIO17 for Start Button
reaction_button = Button(17)  # Same button used for reaction
buzzer = Buzzer(18)  # GPIO18 for Buzzer

# Reaction Time Test
reaction_times = []

def run_test():
    print("Start the drowsy driving test.")
    reaction_times.clear()
    slow_reactions = 0
    
    for i in range(3):
        wait_time = random.uniform(1, 5)
        print(f"\nRound {i+1}: Wait for {wait_time:.2f} seconds...")
        
        time.sleep(wait_time)
        
        print("Buzzer ON! React now!")
        buzzer.on()
        start_time = time.time()
        
        # Wait for button press
        reaction_button.wait_for_press()
        end_time = time.time()
        
        buzzer.off()
        
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

# Main Loop
print("Press the button to start the drowsy driving test.")

while True:
    start_button.wait_for_press()
    run_test()

