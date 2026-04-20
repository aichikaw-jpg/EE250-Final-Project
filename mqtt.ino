#include <WiFi.h>
#include <PubSubClient.h>

//Hotspot wifi name and password
const char* ssid = "aichikawInt";
const char* password = "AlanPass123";
//IP address of raspberry pi
const char* mqtt_server = "10.130.28.211";   

//creates the socket
WiFiClient espClient;
PubSubClient client(espClient);

//initialize the variables(may not use all of them will decide later)
unsigned long lastMsg = 0;
float fakeMoisture = 0;
float tempRead = 0;
float pressureRead = 0;
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
  //connect to internet
  setup_wifi();
  //create a mqtt server
  client.setServer(mqtt_server, 1883);
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
    pressureRead = bme.readPressure();
    humidRead = bme.readHumidity() / 100.0F;

    // char moistRes[16];
    char tempRes[16];
    char pressRes[16];
    char humiRes[16];

    // sprintf(moistRes, "%d", fakeMoisture);
    //get the reading and put into string
    sprintf(tempRes, "%d", tempRead);
    sprintf(pressRes, "%d", pressureRead);
    sprintf(humiRes, "%d", humidRead);

    // Serial.print("Publishing fake moisture: ");
    // Serial.println(moistRes);
    // client.publish("plant/soilMoisture", fakeMoisture);

    //print all the readings just to test
    Serial.print("Displaying temperature reading: ");
    Serial.println(tempRes);
    Serial.print("Displaying pressure reading: ");
    Serial.println(pressRes);
    Serial.print("Displaying humidity reading: ");
    Serial.println(humiRes);

    //put into json format for mqtt
    char msg[100];
    snprintf(msg, sizeof(msg), "{\"temperature\":%.2f,\"humidity\":%.2f,\"pressure\":%.2f}",
           temperature, humidity, pressure);

    // Send through MQTT
    client.publish("sensor/bme280", msg);
  }
}