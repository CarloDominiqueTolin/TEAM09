from flask import Flask, jsonify, send_file
import board
from adafruit_bme280 import basic as adafruit_bme280
from datetime import datetime
import random
import time

lst = []
def average(lst): 
    return sum(lst) / len(lst) 

while True:
  lst.append(bme280.temperature)
  print(average(lst),lst)
  if len(lst)==300:
    lst = lst[:-2]
  time.sleep(2)

i2c = board.I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# change this to match the location's pressure (hPa) at sea level
bme280.sea_level_pressure = 1013.25
print("\nTemperature: %0.1f C" % bme280.temperature)
print("Humidity: %0.1f %%" % bme280.relative_humidity)
print("Pressure: %0.1f hPa" % bme280.pressure)
print("Altitude = %0.2f meters" % bme280.altitude)


app = Flask(__name__)

# Sample data
books = [
    {'id': 1, 'title': 'Python Programming', 'author': 'John Smith'},
    {'id': 2, 'title': 'Data Science Handbook', 'author': 'Jane Doe'}
]

# Route to get a specific book by ID
@app.route('/temperature', methods=['GET'])
def get_temp():
    return jsonify({'timestamp':datetime.now(),'temperature':bme280.temperature})
    
# Route to serve an image
@app.route('/image', methods=['GET'])
def get_image():
    # Path to the image file
    image_path = 'test.jpg'  # Replace with the actual path to your image
    
    # Return the image file
    return send_file(image_path, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
