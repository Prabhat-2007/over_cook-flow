Detecting Boiling Overflow (Rapid Foam & Rim Crossing)
Technique: HSV Color Segmentation + Motion Thresholding.
How it works: When pots boil over, boiling foam is noticeably lighter and higher in saturation/value (white/light grey/bubbly) compared to the surrounding dark pot rim.
We define a circular Region of Interest (ROI) around the outer rim of the cookware. When high-contrast, fast-moving white contours cross out of the inner circle into the outer rim zone, the overflow state triggers.

Detecting Overcooking / Burning (Color & Texture Drift)
Technique: Histograms / Mean Color Shifts in HSV Space.
How it works: Food drying out and charring experiences a distinct, irreversible color shift (e.g sauces turn from bright red/yellow to dark brown/black, or solid foods darken and lose moisture reflection).
We define an ROI covering the center inside of the pot. If the mean brightness (V in HSV) drops below a threshold for a sustained period while saturation (S) changes drastically, the overcook alarm is raised.


pot_monitor.py
Step 1: Image Capture & PreprocessingReads a video frame from the camera.
Resizes it to 640x480 pixels so the processor runs smoothly without lagging.
Converts BGR to HSV: Standard camera frames use RGB (Red, Green, Blue), which is terrible for color detection under changing kitchen lights. 
The script converts it to HSV (Hue, Saturation, Value), which isolates color tone (H) from brightness (V).

Step 2: Overflow Detection (Rim ROI)Creates a "Donut" Ring (Mask): The code draws an invisible circle around the outer rim of your pot (Radius 110px to 150px). Everything inside or outside this ring is ignored.
Filters for Foam: It scans only that ring for pixels matching light/white foam (Low Saturation, High Brightness/Value).
Counts Pixels: If the white/foamy pixel count inside the rim exceeds FOAM_PIXEL_THRESHOLD (2,500 pixels), it flags an Overflow.

Step 3: Overcook / Burning Detection (Food ROI)Creates a Center Circle (Mask): The code draws a circular zone right over the middle of the pot (Radius 90px).
Filters for Char/Darkness: It scans that zone for very dark or black pixels (Value/Brightness near 0).
Calculates the Ratio: It divides dark pixels by the total food area. If more than 65% (DARK_PIXEL_RATIO) of the food turns dark/charred, it flags Overcooking.

Step 4: Decision & CommunicationOnce the thresholds are evaluated, the script draws colored debug overlays on the screen and sends a single character over the internal bridge to the microcontroller:
'O' = Overflow detected (Danger)
'C' = Overcook detected (Warning)
'S' = Everything is Safe


STM32 MCU

Listens to Serial: It checks Serial.available().
Reads the Command:
Received 'O' (Overflow): Immediately sounds a high-pitched 2000Hz continuous warning tone on the buzzer and switches digital Pin 7 (Relay) LOW to automatically cut power to an electric stove or induction cooktop.
Received 'C' (Overcook): Beeps the buzzer on and off (1000Hz pulse) to alert you to check the pot.
Received 'S' (Safe): Silences the buzzer and keeps the relay energized/ON.
