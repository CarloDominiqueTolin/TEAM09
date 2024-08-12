import serial
import pynmea2
from geopy.distance import distance

def parse_gpgga(sentence):
    if sentence.sentence_type == "GPGGA":
        return sentence.latitude, sentence.longitude, sentence.altitude
    return None

def parse_gpgsv(sentence):
    if sentence.sentence_type == "GPGSV":
        return sentence.num_messages, sentence.msg_num, sentence.sv_prn_num, sentence.elevation, sentence.azimuth, sentence.snr
    return None

def compute_location(gpgga_data, gpgsv_data):
    if gpgga_data and gpgsv_data:
        latitude, longitude, altitude = gpgga_data
        return latitude, longitude, altitude
    return None

def main():
    # Replace "/dev/ttyUSB0" with the actual serial port of your GPS device
    ser = serial.Serial("/dev/ttyS0", 9600, timeout=5.0)

    try:
        while True:
            line = ser.readline().decode("utf-8")
            
            try:
                sentence = pynmea2.parse(line)
            except pynmea2.ParseError:
                continue

            gpgga_data = parse_gpgga(sentence)
            gpgsv_data = parse_gpgsv(sentence)
            
            print(gpgsv_data)
            #if gpgga_data and gpgsv_data:
            #    location = compute_location(gpgga_data, gpgsv_data)
            #    print("Current Location:", location)
                
    except KeyboardInterrupt:
        print("Script terminated by user.")

if __name__ == "__main__":
    main()
