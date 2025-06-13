from flask import request, Blueprint, jsonify
from flask_cors import cross_origin
from datetime import datetime
from utils.google_sheets import get_sheets_service

save_bp = Blueprint('save_transaction', __name__)

@save_bp.route('/save-transaction', methods=['POST', 'OPTIONS'])
@cross_origin()
def save_transaction():
    if request.method == 'OPTIONS':
        return '', 200  # CORS preflight response

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    try:
        sheet = get_sheets_service()
        spreadsheet_id = "1FxBCA_JnwtsJgo_sKxFGjg-aFiK9R6JtUR3AfFMyjuk"
        name = data.get('name', '')
        phone = data.get('phone', '')
        address = data.get('address', '')
        total = str(data.get('total', ''))
        cart_items = ', '.join([f"{item['name']} x{item['quantity']}" for item in data.get('cartItems', [])])
        timestamp = data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        values = [[name, phone, address, total, cart_items, timestamp]]
        sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range="Orders!A2",
            valueInputOption="RAW",
            body={"values": values}
        ).execute()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@save_bp.route('/save-transaction-id', methods=['POST', 'OPTIONS'])
@cross_origin()
def save_transaction_id():
    if request.method == 'OPTIONS':
        return '', 200  # CORS preflight response

    data = request.get_json()
    phone = data.get("phone")
    transaction_id = data.get("transactionId")

    if not phone or not transaction_id:
        return jsonify({"error": "Missing data"}), 400

    try:
        sheet = get_sheets_service()
        spreadsheet_id = "1FxBCA_JnwtsJgo_sKxFGjg-aFiK9R6JtUR3AfFMyjuk"
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Orders!A2:G").execute()
        rows = result.get("values", [])

        for idx, row in enumerate(rows):
            if len(row) >= 2 and row[1] == phone:
                row_index = idx + 2
                sheet.values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"Orders!H{row_index}",
                    valueInputOption="RAW",
                    body={"values": [[transaction_id]]}
                ).execute()
                return jsonify({"status": "success"}), 200

        return jsonify({"error": "Order not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
