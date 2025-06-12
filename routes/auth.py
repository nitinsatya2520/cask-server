from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt, datetime
from utils.google_sheets import get_sheets_service

auth_bp = Blueprint("auth", __name__)
SPREADSHEET_ID = "1FxBCA_JnwtsJgo_sKxFGjg-aFiK9R6JtUR3AfFMyjuk"
USERS_RANGE = "Users!A2:D"
SECRET_KEY = "your_secret_key"

def get_all_users():
    sheet = get_sheets_service()
    data = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=USERS_RANGE).execute()
    return data.get("values", [])

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name, email, password = data["name"], data["email"], data["password"]
    users = get_all_users()

    for user in users:
        if user[2] == email:
            return jsonify({"message": "Email already registered"}), 400

    hashed = generate_password_hash(password)
    new_id = str(len(users) + 1)
    new_row = [[new_id, name, email, hashed]]

    sheet = get_sheets_service()
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=USERS_RANGE,
        valueInputOption="RAW",
        body={"values": new_row}
    ).execute()

    return jsonify({"message": "User registered successfully"})

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email, password = data["email"], data["password"]
    users = get_all_users()

    for user in users:
        if user[2] == email and check_password_hash(user[3], password):
            token = jwt.encode({
                "user_id": user[0],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }, SECRET_KEY, algorithm="HS256")
            return jsonify({"token": token})

    return jsonify({"message": "Invalid credentials"}), 401
