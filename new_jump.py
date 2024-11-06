import pyautogui
import numpy as np
import time
import subprocess
import math

# 1. Automatically capture start and end points with a delay
def get_manual_coordinates():
    print("Move the mouse to the start (player position) and wait...")
    time.sleep(3)  # Wait 3 seconds for the user to position the mouse at the start point
    start_x, start_y = pyautogui.position()  # Capture start point
    print(f"Start coordinates: ({start_x}, {start_y})")

    print("Now move the mouse to the end (target position) and wait...")
    time.sleep(3)  # Wait 3 seconds for the user to position the mouse at the end point
    end_x, end_y = pyautogui.position()  # Capture end point
    print(f"End coordinates: ({end_x}, {end_y})")
    
    return (start_x, start_y), (end_x, end_y)

# 2. Calculate the distance between the start and end points
def calculate_distance(start_pos, end_pos):
    return math.sqrt((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2)

# 3. Calculate the press time based on the distance
def calculate_press_time(distance):
    press_time = int(distance * 2.3)  # Adjust this scaling factor as necessary
    print(f"Calculated press time: {press_time} ms based on distance: {distance}")
    return press_time

# 4. Simulate the press action to jump (ADB swipe for Android devices)
def press_for_jump(press_time):
    x1, y1 = 500, 500  # Starting coordinates for the swipe (adjust this based on your screen resolution/game)
    # Use ADB to simulate a swipe on Android device
    subprocess.run(["D:\\jump_game\\scrcpy-win64-v2.7\\adb.exe", "shell", "input", "swipe", str(x1), str(y1), str(x1), str(y1), str(press_time)])
    print(f"Jump performed with press time: {press_time} ms.")

# 5. Main function that controls the flow of the program in a loop
def main():
    print("Welcome to the Jump Game Automation!")
    while True:
        start_pos, end_pos = get_manual_coordinates()  # Get user-selected coordinates with delay
        distance = calculate_distance(start_pos, end_pos)  # Calculate the distance
        press_time = calculate_press_time(distance)  # Calculate the press time based on the distance
        press_for_jump(press_time)  # Perform the jump based on calculated press time
        
        print("Jump completed. Preparing for the next jump...")
        time.sleep(3)  # Wait a bit before the next cycle to avoid rapid loops

if __name__ == "__main__":
    main()
