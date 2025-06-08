import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

# Load the dataset
df = pd.read_csv("safety.csv")  # Replace with your actual CSV file

# Extract Latitude and Longitude from GPS Coordinates
df[['Latitude', 'Longitude']] = df['GPS Coordinates'].str.extract(r'\(([^,]+),\s*([^)]+)\)').astype(float)

# Clean Response Outcome column
df['Response Outcome'] = df['Response Outcome'].str.strip()  # Remove whitespace

# Only keep rows where outcome is "In Progress" or "Resolved"
df = df[df['Response Outcome'].isin(['In Progress', 'Resolved'])]

# Map target values
df['Response Outcome'] = df['Response Outcome'].map({'In Progress': 1, 'Resolved': 0})

# Drop rows with NaNs (just in case)
df = df.dropna(subset=['Latitude', 'Longitude', 'Response Outcome'])

# Feature and target
X = df[['Latitude', 'Longitude']]
y = df['Response Outcome']

# Train model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)

# Save model and features template
joblib.dump(clf, "model.pkl")
X.iloc[0:1].to_csv("model_features.csv", index=False)

print("✅ Model trained and saved successfully.")
