#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

//get the pins for the bme280
#define SDA_PIN 21
#define SCL_PIN 22

//Hotspot wifi name and password
const char* ssid = "aichikawInt";
const char* password = "AlanPass123";
//IP address of raspberry pi
const char* mqtt_server = "10.94.83.211";   

//creates the socket
WiFiClient espClient;
PubSubClient client(espClient);

//creates the bme280 object
Adafruit_BME280 bme;

//initialize the variables(may not use all of them will decide later)
unsigned long lastMsg = 0;
float fakeMoisture = 0;
float tempRead = 0;
// float pressureRead = 0;
float humidRead = 0;


//AI was used for this
//Connects the esp32 to the mobile hotspot
void setup_wifi() {
  //delay for 10 milliseconds
  delay(10);

  //connect to the internet
  WiFi.begin(ssid, password);

  //delay for 500 milliseconds of the wifi is not connected
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  //say if it is connected
  Serial.println();
  Serial.println("WiFi connected");
}

//Connects the esp32 to the raspberry pi with the mqtt
//AI was used to set up the mqtt connection
void reconnect() {
  //if the esp32 is not connected to the raspberry pi try again
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");

    if (client.connect("ESP32_Test_Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 2 seconds");
      delay(2000);
    }
  }
}


void setup() {
  //send at 115200 bits per second
  Serial.begin(115200);
  delay(1000);
  //connect to internet
  setup_wifi();
  //create a mqtt server
  client.setServer(mqtt_server, 1883);

  //get the sensors started
  Wire.begin(SDA_PIN, SCL_PIN);

  //AI was used for this
  if (!bme.begin(0x76)){
    Serial.println("Trying 0x77...");
    if(!bme.begin(0x77)) {
      Serial.println("Could not find the sensor");
      while(1);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 3000) {   // publish every 3 seconds
    lastMsg = now;

    //Get the readings
    tempRead = bme.readTemperature();
    // pressureRead = bme.readPressure() / 100.0F;
    humidRead = bme.readHumidity();

    //print all the readings just to test
    Serial.print("Displaying temperature reading: ");
    Serial.println(tempRead);
    // Serial.print("Displaying pressure reading: ");
    // Serial.println(pressureRead);
    Serial.print("Displaying humidity reading: ");
    Serial.println(humidRead);

    //put into json format for mqtt
    char msg[128];
    snprintf(msg, sizeof(msg), "{\"temperature\":%.2f,\"humidity\":%.2f}",
           tempRead, humidRead);

    Serial.print("Publishing: ");
    Serial.println(msg);

    // Send through MQTT
    client.publish("sensor/bme280", msg);
  }
}