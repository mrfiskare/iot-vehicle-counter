/* 
 *  DHT22: https://create.arduino.cc/projecthub/mafzal/temperature-monitoring-with-dht22-arduino-15b013 
*/

//Libraries
#include <DHT.h>;

//Constants
#define DHTPIN 7  // what pin we're connected to
#define DHTTYPE DHT22 // DHT 22  (AM2302)
DHT dht(DHTPIN, DHTTYPE); // Initialize DHT sensor for normal 16mhz Arduino

//Variables
float hum;  //Stores humidity value
float temp; //Stores temperature value

// Put your setup code here, to run once
void setup() 
{
  Serial.begin(9600);
  dht.begin();
}

// put your main code here, to run repeatedly:
void loop() 
{
  // 2 sec. delay required my dht22
  delay(2500);
  
  //Read data and store it to variables hum and temp
  hum = dht.readHumidity();
  temp= dht.readTemperature();
  
  //Print temp and humidity values to serial monitor
  Serial.print("Humidity: ");
  Serial.print(hum);
  Serial.print(" %, Temp: ");
  Serial.print(temp);
  Serial.println(" Celsius");
}
