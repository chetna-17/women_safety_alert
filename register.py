from flask import Flask, request, jsonify
import pandas as pd
import os
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

CSV_FILE = 'contacts.csv'

# Ensure CSV exists with headers
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=[
        "UserID", "Username", "UserEmail", "AppPassword", 
        "ContactName", "ContactEmail"
    ]).to_csv(CSV_FILE, index=False)
from flask import send_file

@app.route('/')
def serve_form():
    return send_file('register.html')


@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        if not all([data.get("username"), data.get("user_email"), data.get("app_password"),
                    data.get("contact_name"), data.get("contact_email")]):
            return jsonify({"status": "error", "message": "All fields are required"}), 400

        df = pd.read_csv(CSV_FILE)
        new_user_id = int(df["UserID"].max()) + 1 if not df.empty else 1

        new_entry = {
            "UserID": new_user_id,
            "Username": data["username"],
            "UserEmail": data["user_email"],
            "AppPassword": data["app_password"],
            "ContactName": data["contact_name"],
            "ContactEmail": data["contact_email"]
        }

        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

        return jsonify({"status": "success", "user_id": new_user_id}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5001, debug=True)
