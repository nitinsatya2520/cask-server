from flask import Blueprint, request, jsonify
from utils.google_sheets import get_sheets_service
from utils.auth_utils import admin_required
import json
from utils.auth_utils import create_jwt_token


admin_bp = Blueprint("admin", __name__)
SPREADSHEET_ID = "1FxBCA_JnwtsJgo_sKxFGjg-aFiK9R6JtUR3AfFMyjuk"
PRODUCTS_RANGE = "Products!A2:G"




# ➕ Add new product
@admin_bp.route("/admin/add-product", methods=["POST"])
@admin_required
def add_product():
    data = request.get_json()
    required_fields = ["name", "image_url", "description", "price", "stock", "category"]

    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing product fields"}), 400

    sheet = get_sheets_service()
    existing = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=PRODUCTS_RANGE).execute()
    rows = existing.get("values", [])
    new_id = str(len(rows) + 1)

    new_row = [[
        new_id,
        data["name"],
        data["image_url"],
        data["description"],
        str(data["price"]),
        str(data["stock"]),
        data["category"]
    ]]

    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=PRODUCTS_RANGE,
        valueInputOption="RAW",
        body={"values": new_row}
    ).execute()

    return jsonify({"message": "Product added successfully"}), 201

# ✏️ Edit existing product
@admin_bp.route("/admin/edit-product/<product_id>", methods=["PUT"])
@admin_required
def edit_product(product_id):
    data = request.get_json()
    sheet = get_sheets_service()

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=PRODUCTS_RANGE).execute()
    rows = result.get("values", [])
    updated = False

    for i, row in enumerate(rows):
        if row[0] == product_id:
            # Ensure row has at least 7 fields
            while len(row) < 7:
                row.append("")

            for j, key in enumerate(["id", "name", "image_url", "description", "price", "stock", "category"]):
                if key in data and key != "id":
                    row[j] = str(data[key])
            rows[i] = row
            updated = True
            break

    if not updated:
        return jsonify({"message": "Product not found"}), 404

    sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range=PRODUCTS_RANGE).execute()
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=PRODUCTS_RANGE,
        valueInputOption="RAW",
        body={"values": rows}
    ).execute()

    return jsonify({"message": "Product updated successfully"}), 200

# ❌ Delete a product
@admin_bp.route("/admin/delete-product/<product_id>", methods=["DELETE"])
@admin_required
def delete_product(product_id):
    sheet = get_sheets_service()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=PRODUCTS_RANGE).execute()
    rows = result.get("values", [])

    new_rows = [row for row in rows if row[0] != product_id]
    if len(new_rows) == len(rows):
        return jsonify({"message": "Product not found"}), 404

    # Clear and update
    sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range=PRODUCTS_RANGE).execute()

    if new_rows:
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=PRODUCTS_RANGE,
            valueInputOption="RAW",
            body={"values": new_rows}
        ).execute()

    return jsonify({"message": "Product deleted successfully"}), 200

# 📁 admin_routes.py
@admin_bp.route("/admin/orders", methods=["GET"])
@admin_required
def get_orders():
    sheet = get_sheets_service()
    orders_range = "Orders!A2:G"  # Adjust as per your Sheet structure
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=orders_range).execute()
    rows = result.get("values", [])

    orders = []
    for row in rows:
        orders.append({
            "name": row[0] if len(row) > 0 else "",
            "phone": row[1] if len(row) > 1 else "",
            "address": row[2] if len(row) > 2 else "",
            "cartItems": json.loads(row[3]) if len(row) > 3 else [],
            "total": row[4] if len(row) > 4 else "",
            "timestamp": row[5] if len(row) > 5 else "",
            "transactionId": row[7] if len(row) > 7 else "",
        })

    return jsonify(orders), 200

@admin_bp.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    if data.get("password") == "Nitin":
        token = create_jwt_token(user_id="admin_user", role="admin")
        return jsonify({"token": token})
    else:
        return jsonify({"message": "Unauthorized"}), 401

