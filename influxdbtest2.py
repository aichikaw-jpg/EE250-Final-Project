import json
import pandas as pd
import joblib
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

print("imports done")

print("loading model")
#loads the machine learning models
stress_model = joblib.load("plant_stress_model.pkl")
thresholds = joblib.load("plant_thresholds.pkl")
print("model and threshold finished loading")

print("setting up influx")
#sets up the influxdb
#change to laptop IP if influxdb is supposed to be run on the laptop
INFLUX_HOST = "10.94.83.122"     
#sets the influxdb port
INFLUX_PORT = 8086
INFLUX_DB = "plant_data"

#creates an influxdb client that connects to the influxdb server
#uses the influxdb host and port that was given earlier
#uses the username and password (which was admin and password in my case from the previous tig lab)
#ssl=true uses https instead of http
#verify_ssl=False allows it to not check for a certificate
influx_client = InfluxDBClient(
    host=INFLUX_HOST,
    port=INFLUX_PORT,
    username="admin",
    password="password",
    ssl=True,
    verify_ssl=False
)

print("creating database")
# create database if needed
influx_client.create_database(INFLUX_DB)
influx_client.switch_database(INFLUX_DB)
print("influx setup finished")

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

def environment_status_code(env_status):
    mapping = {
	"STABLE CONDITIONS": 0,
	"MONITOR CONDITIONS": 1,
	"MODERATE WATER DEMAND": 2,
	"HIGH WATER DEMAND": 3
    }
    return mapping.get(env_status, -1)

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
	"environment_status_code": environment_status_code(env_status),
        "stress_level": stress_level,
        "stress_score": float(stress_score),
        "stress_level_code": stress_level_code(stress_level)
    }

# --------------------------------------------------
# 7. WRITE TO INFLUXDB
# --------------------------------------------------
def write_to_influx(result):
    json_body = [
        {
            "measurement": "plant_monitor",
            "tags": {
                "environment_status": result["environment_status"],
                "stress_level": result["stress_level"]
            },
            "fields": {
                "temperature": float(result["temperature"]),
                "humidity": float(result["humidity"]),
                "stress_score": float(result["stress_score"]),
                "stress_level_code": int(result["stress_level_code"]),
		"environment_status_code": int(result["environment_status_code"])
            }
        }
    ]

    influx_client.write_points(json_body)

# --------------------------------------------------
# 8. MQTT SETTINGS
# --------------------------------------------------
MQTT_BROKER = "10.94.83.211"
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

print("About to connect to Mqtt Broker...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

print("Waiting for MQTT messages...")
client.loop_forever()
