import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------
df = pd.read_csv("Indoor_Plant_Health_and_Growth_Factors.csv")
df.columns = df.columns.str.strip()

df = df[[
    "Room_Temperature_C",
    "Humidity_%"
]].dropna().copy()

print("Dataset shape:", df.shape)

# --------------------------------------------------
# 2. DATA-DRIVEN THRESHOLDS
# --------------------------------------------------
temp_mild_hot = df["Room_Temperature_C"].quantile(0.65)
temp_hot = df["Room_Temperature_C"].quantile(0.80)
temp_very_hot = df["Room_Temperature_C"].quantile(0.90)

hum_low = df["Humidity_%"].quantile(0.35)
hum_very_low = df["Humidity_%"].quantile(0.20)

print("\nTemperature thresholds:")
print("Mild hot :", temp_mild_hot)
print("Hot      :", temp_hot)
print("Very hot :", temp_very_hot)

print("\nHumidity thresholds:")
print("Low      :", hum_low)
print("Very low :", hum_very_low)

# --------------------------------------------------
# 3. COMBINED THRESHOLD LOGIC
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
# 4. TRAIN ML MODEL
# --------------------------------------------------
stress_model = IsolationForest(
    n_estimators=200,
    contamination=0.03,
    random_state=42
)
stress_model.fit(df)

# --------------------------------------------------
# 5. SAVE MODEL + THRESHOLDS
# --------------------------------------------------
thresholds = {
    "temp_mild_hot": temp_mild_hot,
    "temp_hot": temp_hot,
    "temp_very_hot": temp_very_hot,
    "hum_low": hum_low,
    "hum_very_low": hum_very_low
}

joblib.dump(stress_model, "plant_stress_model.pkl")
joblib.dump(thresholds, "plant_thresholds.pkl")

print("\nModel and thresholds saved successfully.")
