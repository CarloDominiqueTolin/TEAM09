import subprocess

command = "rpicam-still --encoding png --output sky.png --immediate"
output = subprocess.check_output(command, shell=True)
print(output)
