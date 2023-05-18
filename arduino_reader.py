import serial
import json


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

    def _read_from_arduino(self):
        if self.serial_data.inWaiting():
            arduino_data = self.serial_data.readline().decode('utf-8').strip()
            self.measurement = json.loads(arduino_data)

    def get_measurement_id(self):
        self._read_from_arduino()
        return self.measurement["measurement_id"]

    def get_co2_sensor(self):
        self._read_from_arduino()
        return self.measurement["carbon_monoxide"]

    def get_air_quality_sensor(self):
        self._read_from_arduino()
        return self.measurement["air_quality"]

    def get_all_sensors(self, timestamp):
        self._read_from_arduino()
        self.measurement['timestamp'] = timestamp
        return json.dumps(self.measurement)


# Test
arduino = ArduinoReader('/dev/ttyACM0', 9600)
print(arduino.get_measurement_id())
print(arduino.get_co2_sensor())
print(arduino.get_air_quality_sensor())
print(arduino.get_all_sensors('2023-05-18_14-30'))
