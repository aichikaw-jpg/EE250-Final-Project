import pandas as pd
import joblib
import json

# --------------------------------------------------
# 1. LOAD MODEL + THRESHOLDS
# --------------------------------------------------
stress_model = joblib.load("plant_stress_model.pkl")
thresholds = joblib.load("plant_thresholds.pkl")

# --------------------------------------------------
# 2. RULE-BASED LOGIC
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
# 3. ML ASSESSMENT
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
# 4. FULL SYSTEM (NO PRESSURE)
# --------------------------------------------------
def plant_system(temp, humidity):
    env_status = decide_environment_status(temp, humidity, thresholds)
    stress_level, stress_score = assess_stress_level(temp, humidity)

    return {
        "temperature": temp,
        "humidity": humidity,
        "environment_status": env_status,
        "stress_level": stress_level,
        "stress_score": stress_score
    }

# --------------------------------------------------
# 5. MQTT HANDLER (CLEAN VERSION)
# --------------------------------------------------
def on_message(client, userdata, msg):
    if msg.topic == "sensor/bme280":
        data = json.loads(msg.payload.decode())

        temp = data["temperature"]
        humidity = data["humidity"]

        result = plant_system(temp, humidity)

        print("Result:", result)