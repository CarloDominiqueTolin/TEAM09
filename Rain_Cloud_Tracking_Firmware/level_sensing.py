import mpu6050
import time
import math

# Create a new Mpu6050 object
mpu6050 = mpu6050.mpu6050(0x68)

# Define tolerance for being level (in degrees)
tolerance = 2

# Define a function to read the sensor data and check if it is level
def is_sensor_level():
    # Read the accelerometer values
    accelerometer_data = mpu6050.get_accel_data()

    # Calculate pitch and roll angles (in degrees)
    pitch = math.atan2(accelerometer_data['y'], math.sqrt(accelerometer_data['x']**2 + accelerometer_data['z']**2)) * (180/math.pi)
    roll = math.atan2(-accelerometer_data['x'], accelerometer_data['z']) * (180/math.pi)

    # Check if pitch and roll angles are within tolerance for being level
    if abs(pitch) <= tolerance and abs(roll) <= tolerance:
        return True, pitch, roll
    else:
        return False, pitch, roll

# Start a while loop to continuously check if the sensor is level
while True:
    # Check if the sensor is level
    is_level, pitch, roll = is_sensor_level()

    # Print the result
    if is_level:
        print("Sensor is level.")
        print("Pitch:", pitch, "degrees")
        print("Roll:", roll, "degrees")
    else:
        print("Sensor is not level.")
        print("Pitch:", pitch, "degrees")
        print("Roll:", roll, "degrees")

    # Wait for 1 second
    time.sleep(1)