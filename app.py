from flask import Flask
from routes.auth import auth_bp
from routes.products import products_bp
from routes.admin import admin_bp
from flask_cors import CORS
from dotenv import load_dotenv
import os
from routes.save_transaction import save_bp

app = Flask(__name__)
load_dotenv()  # Load env variables

# ✅ Correct CORS setup for frontend at localhost:3000
CORS(app, supports_credentials=True, expose_headers=["Authorization"]})

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(products_bp, url_prefix="/api")
app.register_blueprint(admin_bp, url_prefix="/api")
app.register_blueprint(save_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True)
