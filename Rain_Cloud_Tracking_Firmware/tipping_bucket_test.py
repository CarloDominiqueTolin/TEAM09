import RPi.GPIO as GPIO
import time

SENSOR_PIN = 5

# Rainfall amount per tip in millimeters
RAIN_PER_TIP = 0.2000  # Example: 0.2000 mm per tip 

# Initialize the tipping count and total rainfall
tip_count = 0
total_rainfall = 0.0

# Set up the GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#if error https://stackoverflow.com/questions/75542224/runtimeerror-failed-to-add-edge-detection-on-raspberrypi

def tip_detected(channel):
    global tip_count, total_rainfall
    tip_count += 1
    total_rainfall = tip_count * RAIN_PER_TIP
    print(f"Tip count: {tip_count}, Total Rainfall: {total_rainfall:.2f} mm")

# Add event detection for the sensor pin
GPIO.add_event_detect(SENSOR_PIN, GPIO.FALLING, callback=tip_detected, bouncetime=500)

try:
    print("Rainfall measurement started. Press Ctrl+C to stop.")
    while True:
        # Keep the program running to detect tips
        time.sleep(1)
except KeyboardInterrupt:
    print("Measurement stopped by user.")
finally:
    GPIO.cleanup()