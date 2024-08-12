import time
import argparse
import requests
import board
from adafruit_bme280 import basic as adafruit_bme280
import datetime
import time
import subprocess

# Log file path (same as the one used in the system-wide script)
log_file_path = 'rainfall_log.txt'

def get_system_time():
    result = subprocess.run(["date", "+%Y-%m-%dT%H:%M:%S"], capture_output=True, text=True)
    return result.stdout.strip()

def read_log_file():
    """Read the log file and print the total rainfall."""
    try:
        with open(log_file_path, 'r') as log_file:
            content = log_file.read().strip()
            if content:
                # Extract total rainfall from the content
                parts = content.split(', ')
                if len(parts) > 2:
                    total_rainfall = parts[2].split(': ')[1]
                    return float(total_rainfall.split(' ')[0])
                else:
                    print("Log format incorrect.")
                    return 0
            else:
                print("Log file is empty.")
                return 0
    except FileNotFoundError:
        print("Log file not found.")
        return 0
    except Exception as e:
        print(f"Error reading log file: {e}")
        return 0

# Initialize I2C
i2c = board.I2C()
#BME280 Object
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
                      
def runWeatherSensors(device_id,api_url):
    try:
        data = {
                "device_id" : device_id,
                "rainfall_amount" : read_log_file(),
                "air_temperature" : round(bme280.temperature,2),
                "humidity" : round(bme280.relative_humidity,2),
                "pressure" : round(bme280.pressure,2),
                "timestamp" : datetime.datetime.now().replace(microsecond=0).isoformat()
                #"timestamp":get_system_time()
            }
        
        x = requests.post(
            f"{api_url}/log-weather-data", 
            json = data
        )
        print(data)
        time.sleep(2)
    except Exception as e:
        print(e)
    
    
parser = argparse.ArgumentParser()

parser.add_argument('--device_id', type=int, help='Device ID')
parser.add_argument('--api_url', type=str, help='API URL')

args = parser.parse_args()
device_id = args.device_id
api_url = args.api_url

print("Rainfall measurement started.")
try:
    while True:
        runWeatherSensors(device_id,api_url)
finally:
    GPIO.cleanup()
    
#python weather_sensors.py --device_id 1 --api_url https://83aa-136-158-10-96.ngrok-free.app

