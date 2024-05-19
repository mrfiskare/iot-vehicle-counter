import json
import serial
import time
import signal
import sys
import os

class ArduinoReader:
    def __init__(self, serial_port='/dev/ttyACM0', baud_rate=9600):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.serial_data = serial.Serial(serial_port, baud_rate)
        self.measurement = {
            "carbon_monoxide": 0,
            "air_quality": 0
        }

    def read_from_arduino(self, timestamp):
        arduino_data = self.serial_data.readline().decode('utf-8').strip()
        measurement_dict = json.loads(arduino_data)
        self.measurement["carbon_monoxide"] = measurement_dict["carbon_monoxide"]
        self.measurement["air_quality"] = measurement_dict["air_quality"]
        self.measurement['timestamp'] = timestamp
        return json.dumps(self.measurement)

    def save_to_file(self, data):
        json_folder = "/home/pi/json"
        json_file = "sensors.json"

        if not os.path.exists(json_folder):
            os.makedirs(json_folder)

        json_path = os.path.join(json_folder, json_file)

        data = []

        if os.path.exists(json_path):
            with open(json_path, 'r') as file:
                data = json.load(file)

        data.append({
            'timestamp': self.measurement['timestamp'],
            'air_quality': self.measurement["air_quality"],
            'carbon_monoxide': self.measurement["carbon_monoxide"]
        })

        with open(json_path, 'w') as file:
            json.dump(data, file, indent=4)
            file.close()


        print("Data saved to sensors.json")

    def close(self):
        self.serial_data.close()


# Function to handle keyboard interrupt
def handle_interrupt(signal, frame):
    print("Keyboard interrupt detected. Closing the serial port...")
    arduino.close()
    sys.exit(0)


if __name__ == "__main__":

    # Register the interrupt signal handler
    signal.signal(signal.SIGINT, handle_interrupt)

    arduino = ArduinoReader('/dev/ttyACM0', 9600) 
    timestamp = time.strftime("2023-05-18_19-22")

    try:
        arduino.save_to_file(arduino.read_from_arduino(timestamp))
       

    except KeyboardInterrupt:
        # Handle keyboard interrupt
        print("Keyboard interrupt detected. Closing the serial port...")
        arduino.close()
