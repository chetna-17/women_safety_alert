# 👩‍💻 Women Safety Alert System

A machine learning–enabled web application that enhances women's safety by predicting emergency response outcomes and sending real-time panic alerts via email.  

## 🚀 Features

### 1. 🔍 **Incident Outcome Prediction**
- Trains a **Random Forest Regression model** with an accuracy of **0.92**
- Predicts **response outcome probability** based on incident **location**
- Trained using the `safety.csv` dataset from [Kaggle](https://kaggle.com)

### 2. 📝 **User Registration**
- A simple web interface to register users
- Stores user details (including email and app password) in a local `contacts.csv` file

### 3. 🚨 **Panic Alert System**
- Accepts **location** and **user ID** as input via a panic form
- Performs **real-time prediction** using the trained model (`model.pkl`)
- Sends **alert emails** to the registered contact with:
  - Victim’s location
  - Predicted response outcome probability
  - Date and time of the incident

### 4. 🗺️ **Map-Based Alert Visualization**
- Displays:
  - Victim’s live location
  - Nearest police station
  - Prediction confidence
  - Timestamp
- Implemented in `alert_map.html`

### 5. 🧾 **Incident Logging**
- All panic alert submissions are logged in `panic_alert_logs.csv` with:
  - Date & time
  - Latitude & longitude
  - Predicted probability
  - Victim ID

---

## 📁 Folder Structure

women_safet_alert/
├── app.py # Main app file
├── register.py # Handles user registration
├── trainmodel.py # Trains the Random Forest model
├── model.pkl # Trained model file
├── model_features.csv # Feature list used in model
├── panic_alert_logs.csv # Logs of panic alert submissions
├── contacts.csv # Stores registered user emails (excluded from Git)
├── testemail.py # Email test script (excluded from Git)
├── sample/
│ ├── register.py # Registration route logic
│ ├── panic_form.html # Panic button input form
│ └── alert_map.html # Map output for alerts
├── .gitignore # Ensures private files aren't tracked
