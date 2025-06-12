# routes/products.py
from flask import Blueprint, jsonify
from utils.google_sheets import get_sheets_service

products_bp = Blueprint("products", __name__)

SPREADSHEET_ID = "1FxBCA_JnwtsJgo_sKxFGjg-aFiK9R6JtUR3AfFMyjuk"  # Your actual ID
RANGE = "Products!A2:G"

@products_bp.route("/products", methods=["GET"])
def get_products():
    sheet = get_sheets_service()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE).execute()
    rows = result.get("values", [])

    keys = ["id", "name", "image_url", "description", "price", "stock", "category"]
    products = [dict(zip(keys, row)) for row in rows]

    return jsonify(products)
