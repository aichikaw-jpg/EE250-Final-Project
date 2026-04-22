import json
import pandas as pd
import joblib
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --------------------------------------------------
# 1. LOAD MODEL + THRESHOLDS
# --------------------------------------------------
stress_model = joblib.load("plant_stress_model.pkl")
thresholds = joblib.load("plant_thresholds.pkl")

# --------------------------------------------------
# 2. INFLUXDB SETTINGS
# --------------------------------------------------
INFLUX_URL = "http://localhost:8086"   # use localhost if InfluxDB is on the Pi
INFLUX_TOKEN = "YOUR_INFLUXDB_TOKEN"
INFLUX_ORG = "YOUR_ORG"
INFLUX_BUCKET = "plant_data"

influx_client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# --------------------------------------------------
# 3. RULE-BASED LOGIC
# --------------------------------------------------
def decide_environment_status(temp, humidity, thresholds):
    stress = 0

    if temp >= thresholds["temp_very_hot"]:
        stress += 3
    elif temp >= thresholds["temp_hot"]:
        stress += 2
    elif temp >= thresholds["temp_mild_hot"]:
        stress += 1

    if humidity <= thresholds["hum_very_low"]:
        stress += 3
    elif humidity <= thresholds["hum_low"]:
        stress += 2
    elif humidity <= thresholds["hum_low"] + 5:
        stress += 1

    if stress >= 5:
        return "HIGH WATER DEMAND"
    elif stress >= 3:
        return "MODERATE WATER DEMAND"
    elif stress >= 1:
        return "MONITOR CONDITIONS"
    else:
        return "STABLE CONDITIONS"

# --------------------------------------------------
# 4. ML ASSESSMENT
# --------------------------------------------------
def assess_stress_level(temp, humidity):
    sample = pd.DataFrame([{
        "Room_Temperature_C": temp,
        "Humidity_%": humidity
    }])

    score = stress_model.decision_function(sample)[0]

    if score < 0:
        return "SEVERE STRESS", score
    elif score < 0.05:
        return "ELEVATED STRESS", score
    else:
        return "NORMAL RANGE", score

# --------------------------------------------------
# 5. OPTIONAL NUMERIC CODE FOR GRAFANA
# --------------------------------------------------
def stress_level_code(stress_level):
    mapping = {
        "NORMAL RANGE": 0,
        "ELEVATED STRESS": 1,
        "SEVERE STRESS": 2
    }
    return mapping.get(stress_level, -1)

# --------------------------------------------------
# 6. FULL SYSTEM
# --------------------------------------------------
def plant_system(temp, humidity):
    env_status = decide_environment_status(temp, humidity, thresholds)
    stress_level, stress_score = assess_stress_level(temp, humidity)

    return {
        "temperature": temp,
        "humidity": humidity,
        "environment_status": env_status,
        "stress_level": stress_level,
        "stress_score": float(stress_score),
        "stress_level_code": stress_level_code(stress_level)
    }

# --------------------------------------------------
# 7. WRITE TO INFLUXDB
# --------------------------------------------------
def write_to_influx(result):
    point = (
        Point("plant_monitor")
        .field("temperature", float(result["temperature"]))
        .field("humidity", float(result["humidity"]))
        .field("stress_score", float(result["stress_score"]))
        .field("stress_level_code", int(result["stress_level_code"]))
        .tag("environment_status", result["environment_status"])
        .tag("stress_level", result["stress_level"])
    )

    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

# --------------------------------------------------
# 8. MQTT SETTINGS
# --------------------------------------------------
MQTT_BROKER = "10.94.83.211"     # change if needed
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/bme280"

# --------------------------------------------------
# 9. MQTT CALLBACKS
# --------------------------------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"\nReceived MQTT message: {payload}")

        data = json.loads(payload)

        temp = float(data["temperature"])
        humidity = float(data["humidity"])

        result = plant_system(temp, humidity)

        print("Plant assessment:")
        print(result)

        write_to_influx(result)
        print("Data written to InfluxDB")

    except KeyError as e:
        print(f"Missing expected key in MQTT data: {e}")
    except json.JSONDecodeError:
        print("Message was not valid JSON")
    except Exception as e:
        print(f"Error processing message: {e}")

# --------------------------------------------------
# 10. START MQTT CLIENT
# --------------------------------------------------
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

print("Waiting for MQTT messages...")
client.loop_forever()