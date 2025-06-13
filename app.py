from flask import Flask
from routes.auth import auth_bp
from routes.products import products_bp
from routes.admin import admin_bp
from flask_cors import CORS  # Important if frontend is hosted separately
from dotenv import load_dotenv
import os
from routes.save_transaction import save_transaction

app = Flask(__name__)
CORS(app)  # Allow requests from React frontend
load_dotenv()  # This loads the .env file

# This line will now work:
GOOGLE_SHEETS_CREDS_B64 = os.getenv("GOOGLE_SHEETS_CREDS_B64")
# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(products_bp, url_prefix="/api")
app.register_blueprint(admin_bp, url_prefix="/api")
app.register_blueprint(save_transaction, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True)
