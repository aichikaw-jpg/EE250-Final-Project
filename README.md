# EE250-Final-Project
Jamie Ho, Alan Ichikawa - Chang

Instructions: 
1) Solder pins onto BME280 sensor and connect the sensor to pins on ESP32. The 3v3 pin should be connected to Vin, Gnd to Gnd, SCL to gpio22, and SDA to gpio21.
2) Then, change the mqtt.ino program so that the ssid name, the password, and the mqtt server ip is changed. Change the ssid name to the name of the mobile hotspot that your laptop, esp32, and raspberry pi will be connected to. Change the password to match the same mobile hotspot password. Change the mqtt server ip to have the raspberry pi ip. Make sure that you have downloaded the adafruit bme280 library and the esp32 dev module library on arduino ide. Finally, upload the program to to the esp32 thorugh the arduino ide.
3) Make sure to click the sketch monitor to view the results to check that it is properly connecting to the mqtt and that you can see the results of the sensor.
4) 

