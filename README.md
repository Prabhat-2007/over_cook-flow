Detecting Boiling Overflow (Rapid Foam & Rim Crossing)
Technique: HSV Color Segmentation + Motion Thresholding.
How it works: When pots boil over, boiling foam is noticeably lighter and higher in saturation/value (white/light grey/bubbly) compared to the surrounding dark pot rim.
We define a circular Region of Interest (ROI) around the outer rim of the cookware. When high-contrast, fast-moving white contours cross out of the inner circle into the outer rim zone, the overflow state triggers.

Detecting Overcooking / Burning (Color & Texture Drift)
Technique: Histograms / Mean Color Shifts in HSV Space.
How it works: Food drying out and charring experiences a distinct, irreversible color shift (e.g sauces turn from bright red/yellow to dark brown/black, or solid foods darken and lose moisture reflection).
We define an ROI covering the center inside of the pot. If the mean brightness (V in HSV) drops below a threshold for a sustained period while saturation (S) changes drastically, the overcook alarm is raised.
