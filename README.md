# EE250-Final-Project
Jamie Ho, Alan Ichikawa - Chang

Instructions: 
1) Solder pins onto BME280 sensor and connect the sensor to pins on ESP32. The 3v3 pin should be connected to Vin, Gnd to Gnd, SCL to gpio22, and SDA to gpio21.
2) Then, change the mqtt.ino program so that the ssid name, the password, and the mqtt server ip is changed. Change the ssid name to the name of the mobile hotspot that your laptop, esp32, and raspberry pi will be connected to. Change the password to match the same mobile hotspot password. Change the mqtt server ip to have the raspberry pi ip. Make sure that you have downloaded the adafruit bme280 library and the esp32 dev module library on arduino ide. Finally, upload the program to to the esp32 thorugh the arduino ide.
3) If the program does not run as soon as it is uploaded to the esp32, press the EN button. 
4) Make sure to click the sketch monitor to view the results to check that it is properly connecting to the mqtt and that you can see the results of the sensor.
5) Next, send the plant_stress_model.pkl, plant_thresholds.pkl, and the influxdbtest2.py into the raspberry pi. The plant_stress_model.pkl and plant_thresholds.pkl may not work if the sklearn versions are not the same so they may need to be retrained.
6) (Only do this if the sklearn versions are not the same): Also send mltest3.py and the dataset to the raspberry pi. Create the models: plant_stress_model.pkl and plant_thresholds.pkl onto the raspberry pi. 
7) Now in the influxdbtest2.py, change the INFLUX_HOST to be your laptop ip. In the influx_client, change the username and password to be your influxdb username and password. You can leave it out, if you don't have it. Change the MQTT_BROKER to have your raspberry pi ip.
8) Run the influxdbtest2.py on your raspberry pi by doing python3 influxdbtest2.py
9) On a seperate terminal on your laptop, do sudo systemctl start grafana-server. Go to grafana and upload the given dashboard: Plant Monitor-1776998171411.json
10) Also make sure for the grafana that the data source is editted to have your laptop ip if that is where your influxdb is run

External Libraries used for Arduino IDE: 
WiFi.h, PubSubClient.h, Wire.h, Adafruit_Sensor.h, Adafruit_BME280.h
External Libraries used for mqtt, influxdb, machine learning:
json, pandas, joblib, paho.mqtt.client, and influxdb
