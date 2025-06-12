from flask import Flask
from routes.auth import auth_bp
from routes.products import products_bp
from routes.admin import admin_bp
from flask_cors import CORS  # Important if frontend is hosted separately

app = Flask(__name__)
CORS(app)  # Allow requests from React frontend

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(products_bp, url_prefix="/api")
app.register_blueprint(admin_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True)
