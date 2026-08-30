import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import uvicorn

# =========================================================
# 1. GENERATE A SYNTHETIC DATASET
# =========================================================

np.random.seed(42)
n_samples = 300

df = pd.DataFrame({
    'size_m2': np.random.randint(50, 250, n_samples),
    'bedrooms': np.random.randint(1, 6, n_samples),
    'age': np.random.randint(0, 40, n_samples),
    'distance_city_km': np.random.randint(1, 30, n_samples),
})

# Create target variable with some noise
df['price'] = (
    df['size_m2'] * 2500
    + df['bedrooms'] * 15000
    - df['age'] * 1200
    - df['distance_city_km'] * 2000
    + np.random.normal(0, 20000, n_samples)
)

# Introduce some missing values
df.loc[df.sample(15, random_state=1).index, 'size_m2'] = np.nan
df.loc[df.sample(10, random_state=2).index, 'bedrooms'] = np.nan

print('\n===== FIRST 5 ROWS =====')
print(df.head())

print('\n===== DATA INFO =====')
print(df.info())

print('\n===== MISSING VALUES =====')
print(df.isnull().sum())

# =========================================================
# 2. DATA CLEANING
# =========================================================

features = ['size_m2', 'bedrooms', 'age', 'distance_city_km']
target = 'price'

X = df[features]
y = df[target]

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, features)
    ]
)

# =========================================================
# 3. MODEL PIPELINE
# =========================================================

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', LinearRegression())
])

# =========================================================
# 4. TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================================================
# 5. TRAIN MODEL
# =========================================================

model.fit(X_train, y_train)

# =========================================================
# 6. EVALUATE MODEL
# =========================================================

predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print('\n===== MODEL EVALUATION =====')
print(f'Mean Absolute Error: {mae:,.2f}')
print(f'R² Score: {r2:.4f}')

# =========================================================
# 7. SAVE MODEL
# =========================================================

model_path = Path('house_price_model.pkl')
joblib.dump(model, model_path)

print(f'\nModel saved to: {model_path.resolve()}')

# =========================================================
# 8. FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title='House Price Prediction API',
    description='Predict house prices using a trained ML model',
    version='1.0'
)

# Load model once when API starts
trained_model = joblib.load(model_path)

# Request schema
class HouseFeatures(BaseModel):
    size_m2: float
    bedrooms: float
    age: float
    distance_city_km: float

# Response schema
class PredictionResponse(BaseModel):
    predicted_price: float

@app.get('/')
def root():
    return {
        'message': 'House Price Prediction API is running',
        'endpoints': ['/predict']
    }

@app.post('/predict', response_model=PredictionResponse)
def predict(features: HouseFeatures):
    input_df = pd.DataFrame([{
        'size_m2': features.size_m2,
        'bedrooms': features.bedrooms,
        'age': features.age,
        'distance_city_km': features.distance_city_km
    }])

    prediction = trained_model.predict(input_df)[0]

    return PredictionResponse(
        predicted_price=round(float(prediction), 2)
    )

# =========================================================
# 9. RUN API
# =========================================================

if __name__ == '__main__':
    print('\nStarting FastAPI server...')
    print('Open: http://127.0.0.1:8000/docs')
    uvicorn.run(app, host='127.0.0.1', port=8000)
