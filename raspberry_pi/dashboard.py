import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, f1_score
import joblib
# Load data
data = pd.read_csv("flood_data.csv")
# ❗ REMOVE EMPTY FLOOD VALUES
data = data.dropna(subset=['Flood'])
# Features
X = data[['Temperature', 'Humidity', 'Water_Level', 'Soil']]
# Target
y = data['Flood']
# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
73
# Train
model = RandomForestClassifier()
model.fit(X_train, y_train)
# Predict
y_pred = model.predict(X_test)
# Metrics
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred, zero_division=1))
print("F1 Score:", f1_score(y_test, y_pred, zero_division=1))
# Save
joblib.dump(model, "flood_model.pkl")
print("Model saved")