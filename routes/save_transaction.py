# routes/save_transaction.py
from flask import request, Blueprint, jsonify
from datetime import datetime
from utils.google_sheets import get_sheets_service

save_bp = Blueprint('save_transaction', __name__)

SPREADSHEET_ID = "1FxBCA_JnwtsJgo_sKxFGjg-aFiK9R6JtUR3AfFMyjuk"
ORDER_RANGE = "Orders!A2:G"  # Existing data range (no header)

@save_bp.route('/api/save-transaction', methods=['POST'])
def save_transaction():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    try:
        # Prepare data
        name = data.get('name', '')
        phone = data.get('phone', '')
        address = data.get('address', '')
        total = str(data.get('total', ''))
        cart_items = ', '.join([f"{item['name']} x{item['quantity']}" for item in data.get('cartItems', [])])
        timestamp = data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Append row using Google Sheets API
        sheet = get_sheets_service()
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="Orders!A:G",
            valueInputOption="RAW",
            body={"values": [[name, phone, address, total, cart_items, timestamp]]}
        ).execute()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@save_bp.route('/api/save-transaction-id', methods=['POST'])
def save_transaction_id():
    data = request.get_json()
    phone = data.get("phone")
    transaction_id = data.get("transactionId")

    if not phone or not transaction_id:
        return jsonify({"error": "Missing data"}), 400

    try:
        sheet = get_sheets_service()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=ORDER_RANGE).execute()
        rows = result.get("values", [])

        for idx, row in enumerate(rows):
            if len(row) >= 2 and row[1] == phone:
                row_index = idx + 2  # Adjust for header row
                sheet.values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"Orders!H{row_index}",
                    valueInputOption="RAW",
                    body={"values": [[transaction_id]]}
                ).execute()
                return jsonify({"status": "success"}), 200

        return jsonify({"error": "Order not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
