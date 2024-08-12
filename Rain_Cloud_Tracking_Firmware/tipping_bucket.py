import RPi.GPIO as GPIO
import time
from datetime import datetime

# Define GPIO pin for the photo interrupter
SENSOR_PIN = 5

# Rainfall amount per tip in millimeters (this value should be calibrated for your specific tipping bucket)
RAIN_PER_TIP = 0.2794  # Example: 0.2794 mm per tip (adjust as necessary)

# Initialize the tipping count and total rainfall
tip_count = 0
total_rainfall = 0.0

# Set up the GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Log file path
log_file_path = 'rainfall_log.txt'

def log_rainfall(tip_count, total_rainfall):
    """Log the latest tip count and total rainfall to a file with a timestamp."""
    with open(log_file_path, 'w') as log_file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file.write(f"{timestamp}, Tip count: {tip_count}, Total Rainfall: {total_rainfall:.2f} mm\n")

def tip_detected(channel):
    global tip_count, total_rainfall
    tip_count += 1
    total_rainfall = tip_count * RAIN_PER_TIP
    print(f"Tip count: {tip_count}, Total Rainfall: {total_rainfall:.2f} mm")
    log_rainfall(tip_count, total_rainfall)

# Add event detection for the sensor pin
GPIO.add_event_detect(SENSOR_PIN, GPIO.FALLING, callback=tip_detected, bouncetime=300)

try:
    print("Rainfall measurement started. Press Ctrl+C to stop.")
    while True:
        # Keep the program running to detect tips
        time.sleep(1)
except KeyboardInterrupt:
    print("Measurement stopped by user.")
finally:
    GPIO.cleanup()