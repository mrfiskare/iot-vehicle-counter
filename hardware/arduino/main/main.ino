/*
  Arduino Humidity Sensor: Basic code that demonstrates the usage of Adafruit's libaries with the DHT sensor.
  Code is based off the example code in the DHT library. Created 25/04/2019 By Gus
  Resource: https://pimylifeup.com/arduino-humidity-sensor-dht22/ 
  Requires the following libraries to be installed:
  DHT Sensor Library: https://github.com/adafruit/DHT-sensor-library
  Adafruit Unified Sensor Library : https://github.com/adafruit/Adafruit_Sensor
*/

#include <DHT.h> //Include the DHT library.

#define dhtPin 2 //Define the type data pin
#define DHTType DHT22 //Define the DHT sensor (DHT11, DHT21, or DHT22)

//Instantiate the dht class with our data pin and DHT type.
DHT dht = DHT(dhtPin, DHTType);

void setup() 
{
  Serial.begin(9600); //Start the serial interface on 9600
  dht.begin();   //Call the begin class in the dht object
}

void loop() 
{
  delay(2000); // Delay for 2 seconds as the DHT22 sampling rate is 0.5Hz
  
  float humidity = dht.readHumidity();
  float temp = dht.readTemperature();

  // Check for any errors, if there is, display error and restart.
  if (isnan(humidity) || isnan(temp)) 
  {
    Serial.println("Failed to read from the DHT sensor, check wiring.");
    return;
  }
  
  Serial.print("Humidity: ");
  Serial.print(humidity);
  
  Serial.print("% || Temperature: ");
  Serial.print(temp);
  Serial.print("°C ");
  
  Serial.println();
  delay(10000);
}
