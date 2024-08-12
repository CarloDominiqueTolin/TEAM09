import requests
import time
import argparse
import os
import subprocess

subprocesses = {}


def start_subprocess(name, command):
    process = subprocess.Popen(command)
    subprocesses[name] = process
    print(f"Process '{name}' started")
    
def stop_subprocess(name):
    if name in subprocesses:
        subprocesses[name].terminate()
        print(f"Process '{name}' terminated.")
    else:
        print(f"Process '{name}' not found.")
    
def stop_all_subprocesses():
    for process_key, process in subprocesses.items():
        try:
            process.terminate()
            print(f"Process '{process_key}' terminated.")
        except Exception as e:
            pass
        finally:
            subprocesses[process_key] = None
    
def startDevice(device_id, api_url):
    #System Clock Update
    print("Updating System Clock")
    os.system("sudo date -s \"$(wget -qSO- --max-redirect=0 www.google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z\"") 
    
    #Weather Sensors
    start_subprocess("weather_sensors",[
        'python','weather_sensors.py',
        '--device_id',str(device_id),
        '--api_url',api_url
    ])
    
    #Camera Web Feed
    #start_subprocess("camera_webfeed",[
    #    'python','webfeed.py',
     #   '--device_id',str(device_id),
     #   '--api_url',api_url
    #])
    
    start_subprocess("camera_webfeed",[
        'python','capture.py',
        '--device_id',str(device_id),
        '--api_url',api_url
    ])
    
    
    # if cameraFeed:
    #     #Start Capturing Sky Images
    #     captureProcess = subprocess.Popen(['python', 'capture.py']) 
    # else:
    #     webStreamProcess = subprocess.Popen(['python', 'webstream.py'])
    
    


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--device_id', type=int, help='Device ID')

    args = parser.parse_args()
    device_id = args.device_id
    
    API_URL = 'http://192.168.100.5:5000'

    print("Device ID:", device_id)
    print("API URL:",API_URL)
    
    try:
        startDevice(device_id, API_URL)
        while True:
            command = input("Enter command (stop <process_name> or stop-all): ")
            if command.strip().lower() == 'stop-all':
                stop_all_subprocesses()
                break
            elif command.strip().lower().startswith('stop'):
                _, process_name = command.strip().split(' ', 1)
                stop_subprocess(process_name.strip())
            else:
                print("Invalid command. Use 'stop <process_name>' or 'stop-all'.")
                
    except KeyboardInterrupt:
        stop_all_subprocesses()
        
        
