import cv2
import numpy as np
import serial
import time

# Initialize internal bridge to the STM32 microcontroller
try:
    arduino = serial.Serial('/dev/ttyS0', 115200, timeout=1)
    time.sleep(2) # Wait for serial bridge connection
except Exception as e:
    print(f"Serial bridge warning: {e}")
    arduino = None

cap = cv2.VideoCapture(0)  # Open USB Camera

# Thresholds
FOAM_PIXEL_THRESHOLD = 2500  # Number of foam pixels in Rim ROI to trigger overflow
DARK_PIXEL_RATIO = 0.65      # Ratio of dark/charred pixels to trigger overcook

def send_alert(alert_code):
    """Sends simple commands to STM32: 'O' for Overflow, 'C' for Overcook, 'S' for Safe"""
    if arduino and arduino.is_open:
        arduino.write(alert_code.encode())

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Resize frame for optimal performance on Quad-Core ARM
    frame = cv2.resize(frame, (640, 480))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define ROIs (Adjust coordinates based on your camera position)
    # Center = (320, 240), Inner Radius = 100px (Food zone), Outer Ring = 100px to 140px (Rim zone)
    height, width, _ = frame.shape
    center_x, center_y = width // 2, height // 2

    # Mask 1: RIM ROI (For Overflow Detection)
    rim_mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(rim_mask, (center_x, center_y), 150, 255, thickness=-1)
    cv2.circle(rim_mask, (center_x, center_y), 110, 0, thickness=-1) # Hole in center

    # Detect Boiling White/Light Foam within Rim ROI
    # White/Foam in HSV: Low Saturation (0-50), High Value/Brightness (180-255)
    lower_foam = np.array([0, 0, 180])
    upper_foam = np.array([180, 50, 255])
    foam_mask = cv2.inRange(hsv, lower_foam, upper_foam)
    active_rim_foam = cv2.bitwise_and(foam_mask, foam_mask, mask=rim_mask)
    foam_pixel_count = cv2.countNonZero(active_rim_foam)

    # Mask 2: FOOD ROI (For Overcook/Burning Detection)
    food_mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(food_mask, (center_x, center_y), 90, 255, thickness=-1)

    # Detect Dark/Burnt Pixels in Food ROI
    # Burnt in HSV: Low Value/Brightness (0-50)
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([180, 255, 50])
    dark_mask = cv2.inRange(hsv, lower_dark, upper_dark)
    active_food_dark = cv2.bitwise_and(dark_mask, dark_mask, mask=food_mask)
    
    total_food_pixels = cv2.countNonZero(food_mask)
    dark_food_pixels = cv2.countNonZero(active_food_dark)
    dark_ratio = dark_food_pixels / float(total_food_pixels) if total_food_pixels > 0 else 0

    # Decision Logic
    if foam_pixel_count > FOAM_PIXEL_THRESHOLD:
        status_text = "DANGER: OVERFLOW DETECTED!"
        color = (0, 0, 255)
        send_alert('O') # Overflow command
    elif dark_ratio > DARK_PIXEL_RATIO:
        status_text = "WARNING: OVERCOOK / BURNING!"
        color = (0, 140, 255)
        send_alert('C') # Overcook command
    else:
        status_text = "STATUS: SAFE"
        color = (0, 255, 0)
        send_alert('S') # Safe command

    # UI Annotations for debugging
    cv2.circle(frame, (center_x, center_y), 150, (255, 0, 0), 2) # Outer Rim boundary
    cv2.circle(frame, (center_x, center_y), 90, (0, 255, 255), 2) # Food boundary
    cv2.putText(frame, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    # Display video stream on output
    cv2.imshow("UNO Q Smart Kitchen Vision", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
