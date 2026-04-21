import json
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

# ---------- INFLUXDB SETTINGS ----------
INFLUX_HOST = "localhost"
INFLUX_PORT = 8086
INFLUX_DATABASE = "plant_db"

# ---------- MQTT SETTINGS ----------
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/bme280"

# ---------- CONNECT TO INFLUXDB ----------
influx_client = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT)
influx_client.create_database(INFLUX_DATABASE)
influx_client.switch_database(INFLUX_DATABASE)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print("Failed to connect to MQTT broker, return code:", rc)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        print("Received MQTT message:", payload)

        data = json.loads(payload)

        pressure = float(data["pressure"])
        temperature = float(data.get("temperature", 0))
        humidity = float(data.get("humidity", 0))

        json_body = [
            {
                "measurement": "plant_data",
                "tags": {
                    "device": "esp32"
                },
                "fields": {
                    "pressure": pressure,
                    "temperature": temperature,
                    "humidity": humidity
                }
            }
        ]

        influx_client.write_points(json_body)
        print("Wrote data to InfluxDB")

    except Exception as e:
        print("Error handling message:", e)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_forever()