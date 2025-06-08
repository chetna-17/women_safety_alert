from flask import Flask, request, jsonify, send_file
import pandas as pd
import os
import joblib
from datetime import datetime
from flask_cors import CORS
import folium
from dotenv import load_dotenv, find_dotenv
import smtplib
from email.message import EmailMessage

load_dotenv(find_dotenv(), override=True)

# Constants
LOG_FILE = "panic_alerts_log.csv"
CONTACTS_FILE = "contacts.csv"
MODEL_FILE = "model.pkl"
FEATURES_FILE = "model_features.csv"
FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")

app = Flask(__name__, static_url_path='', static_folder='sample')
CORS(app, resources={r"/*": {"origins": "*"}})


# Load model
try:
    clf = joblib.load(MODEL_FILE)
    print("✅ Model loaded.")
except Exception as e:
    print("❌ Error loading model:", e)
    clf = None

# Load model features
try:
    X_template = pd.read_csv(FEATURES_FILE)
    print("✅ Feature columns loaded.")
except Exception as e:
    print("❌ Error loading features:", e)
    X_template = pd.DataFrame()

def send_email_alert(from_email, app_password, to_email, name, lat, lon):
    msg = EmailMessage()
    msg['Subject'] = f"Panic Alert from {name}"
    msg['From'] = from_email
    msg['To'] = to_email
    msg.set_content(f"Panic Alert triggered by {name}.\n\nLocation: https://www.google.com/maps?q={lat},{lon}")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(from_email, app_password)
            smtp.send_message(msg)
        print("✅ Email alert sent.")
        return True
    except Exception as e:
        print("❌ Email sending failed:", e)
        return False

@app.route('/')
def index():
    return app.send_static_file('panic_form.html')

@app.route('/submit', methods=['POST'])
def submit_alert():
    try:
        data = request.get_json()
        lat = data.get('lat')
        lon = data.get('lon')
        user_id = data.get('user_id')

        if not all([lat, lon, user_id]):
            return jsonify({'status': 'error', 'message': 'Latitude, Longitude, and UserID are required'}), 400

        contacts_df = pd.read_csv(CONTACTS_FILE)
        user_row = contacts_df[contacts_df['UserID'] == int(user_id)]

        if user_row.empty:
            return jsonify({'status': 'error', 'message': 'UserID not found'}), 404

        user_info = user_row.iloc[0]
        from_email = user_info['UserEmail']
        app_password = user_info['AppPassword']
        to_email = user_info['ContactEmail']
        username = user_info['Username']
        contact_name = user_info['ContactName']

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        outcome_text = "N/A"
        probability = "N/A"

        if clf is not None and not X_template.empty:
            input_df = pd.DataFrame(columns=X_template.columns)
            input_df.loc[0] = [0] * len(X_template.columns)
            input_df.at[0, 'Latitude'] = float(lat)
            input_df.at[0, 'Longitude'] = float(lon)
            try:
                prob = clf.predict_proba(input_df)[0][1]
                result = clf.predict(input_df)[0]
                outcome_text = 'Unresolved/In Progress' if result == 1 else 'Resolved'
                probability = round(prob, 2)
            except Exception as e:
                print("⚠️ Prediction error:", e)

        success = send_email_alert(from_email, app_password, to_email, username, lat, lon)

        new_entry = pd.DataFrame([{
            'Username': username,
            'Latitude': lat,
            'Longitude': lon,
            'Timestamp': timestamp,
            'Predicted Outcome': outcome_text,
            'Probability': probability,
            'Success Count': 1 if success else 0
        }])

        if os.path.exists(LOG_FILE):
            new_entry.to_csv(LOG_FILE, mode='a', index=False, header=False)
        else:
            new_entry.to_csv(LOG_FILE, index=False)

        # Save map
        m = folium.Map(location=[float(lat), float(lon)], zoom_start=14)
        folium.Marker(
            location=[float(lat), float(lon)],
            popup=f"Victim Location<br>{timestamp}<br>Outcome: {outcome_text}<br>Prob: {probability}",
            icon=folium.Icon(color="red")
        ).add_to(m)

        try:
            import requests
            overpass_url = "http://overpass-api.de/api/interpreter"
            query = f"""
                [out:json];
                node["amenity"="police"](around:3000,{lat},{lon});
                out;
            """
            response = requests.get(overpass_url, params={'data': query}, timeout=10)
            response.raise_for_status()
            data = response.json()

            for element in data.get('elements', []):
                name = element['tags'].get('name', 'Unnamed Police Station')
                folium.Marker(
                    location=[element['lat'], element['lon']],
                    popup=name,
                    icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(m)

            print(f"✅ Added {len(data['elements'])} police stations to map.")
        except Exception as e:
            print("⚠️ Error fetching police stations (ignored):", e)

        m.save("sample/latest_alert_map.html")

        return jsonify({
            'status': 'success',
            'message': 'Alert received and message sent',
            'delivery': [{"To": to_email, "Delivered": "Yes" if success else "No"}]
        }), 200

    except Exception as e:
        print("💥 Exception:", e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/map')
def view_map():
    map_path = "sample/latest_alert_map.html"
    if os.path.exists(map_path):
        return send_file(map_path)
    else:
        return "<h3>No map available yet.</h3>", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
