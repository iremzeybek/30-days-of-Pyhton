import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from pathlib import Path

# =========================================
# LOAD DATASET
# =========================================

print("Loading dataset...")
df = sns.load_dataset("tips")

# Keep only useful columns
df = df[["total_bill", "tip", "size", "day", "time"]]

# =========================================
# CLEAN DATA
# =========================================

df = df.dropna()
df = df.drop_duplicates()

print("\nDataset shape:", df.shape)
print(df.head())

# =========================================
# SIMPLE ANALYSIS
# =========================================

avg_tip = df["tip"].mean()
avg_bill = df["total_bill"].mean()

print(f"\nAverage bill: {avg_bill:.2f}")
print(f"Average tip : {avg_tip:.2f}")

print("\nAverage tip by day:")
print(df.groupby("day")["tip"].mean())

# =========================================
# FEATURE ENGINEERING
# =========================================

df_encoded = pd.get_dummies(df, columns=["day", "time"], drop_first=True)

X = df_encoded.drop(columns=["tip"])
y = df_encoded["tip"]

feature_columns = X.columns.tolist()

# =========================================
# TRAIN / TEST SPLIT
# =========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# =========================================
# TRAIN MODEL
# =========================================

model = LinearRegression()
model.fit(X_train, y_train)

# =========================================
# EVALUATE MODEL
# =========================================

predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(f"\nMAE      : {mae:.2f}")
print(f"R2 Score : {r2:.2f}")

# =========================================
# SAVE MODEL
# =========================================

model_file = Path("tip_predictor.joblib")

joblib.dump(
    {
        "model": model,
        "features": feature_columns
    },
    model_file
)

print("\nModel saved successfully.")

# =========================================
# FASTAPI APPLICATION
# =========================================

app = FastAPI(
    title="Restaurant Tip Prediction API",
    version="1.0"
)

saved = joblib.load(model_file)
loaded_model = saved["model"]
loaded_features = saved["features"]

# =========================================
# REQUEST MODEL
# =========================================

class TipRequest(BaseModel):
    total_bill: float
    size: int
    day: str
    time: str

# =========================================
# HELPER FUNCTION
# =========================================

def build_input(data: TipRequest):
    row = {
        "total_bill": data.total_bill,
        "size": data.size,
        "day_Sat": 1 if data.day.lower() == "sat" else 0,
        "day_Sun": 1 if data.day.lower() == "sun" else 0,
        "day_Thur": 1 if data.day.lower() == "thur" else 0,
        "time_Dinner": 1 if data.time.lower() == "dinner" else 0,
    }

    input_df = pd.DataFrame([row])

    # Ensure all columns exist
    for col in loaded_features:
        if col not in input_df.columns:
            input_df[col] = 0

    input_df = input_df[loaded_features]

    return input_df

# =========================================
# API ENDPOINTS
# =========================================

@app.get("/")
def home():
    return {
        "message": "Tip Prediction API is running"
    }

@app.get("/summary")
def summary():
    return {
        "rows": int(len(df)),
        "average_bill": round(float(avg_bill), 2),
        "average_tip": round(float(avg_tip), 2),
        "mae": round(float(mae), 2),
        "r2_score": round(float(r2), 2),
    }

@app.post("/predict")
def predict_tip(request: TipRequest):
    input_df = build_input(request)

    prediction = loaded_model.predict(input_df)[0]

    return {
        "predicted_tip": round(float(prediction), 2)
    }

# =========================================
# RUN SERVER
# =========================================

if __name__ == "__main__":
    import uvicorn

    print("\nStarting FastAPI server...")
    print("Open http://127.0.0.1:8000/docs")

    uvicorn.run(app, host="127.0.0.1", port=8000)
