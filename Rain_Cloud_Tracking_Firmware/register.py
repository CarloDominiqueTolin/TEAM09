import requests

api_url = "http://192.168.100.5:5000"

print(requests.post(
    f"{api_url}/register-device", 
    json = {
        "location": {
        "longitude":123.231,
        "latittude":72.12},
        "orientation":{"x":12,"y":6,"z":13}
        }
    )
)