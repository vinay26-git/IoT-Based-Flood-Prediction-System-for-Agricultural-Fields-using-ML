import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# -------- Load data --------
data = pd.read_csv("flood_data.csv")

# -------- Remove missing values --------
data = data.dropna(subset=['Flood'])

# -------- Features & Target --------
X = data[['Temperature', 'Humidity', 'Water_Level', 'Soil']]
y = data['Flood']

# -------- Train model --------
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# -------- Save model --------
joblib.dump(model, "flood_model.pkl")
print("Model ready")