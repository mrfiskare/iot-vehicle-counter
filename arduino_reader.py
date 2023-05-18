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
            "measurement_id": 0,
            "carbon_monoxide": 0,
            "air_quality": 0
        }


    def read_from_arduino(self, timestamp):
        arduino_data = self.serial_data.readline().decode('utf-8').strip()
        self.measurement = json.loads(arduino_data)
        self.measurement['timestamp'] = timestamp
        
        print('\n')
        print(self.measurement)
        
        return json.dumps(self.measurement)
        
        
    def save_to_file(self, data):
        file_path = "/home/pi/json/sensors.json"

        # Create the folder if it doesn't exist
        folder_path = os.path.dirname(file_path)
        os.makedirs(folder_path, exist_ok=True)

        # Check if the file already exists
        file_exists = os.path.isfile(file_path)

        # Determine the write mode based on file existence
        write_mode = "a" if file_exists else "w"

        # Append or create the file and write the data
        with open(file_path, write_mode) as file:
            if file_exists:
                file.write(",\n")

            file.write(data)

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
