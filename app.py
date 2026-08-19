from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from models import db
from extensions import bcrypt, jwt

from auth_routes import auth_bp
from property_routes import property_bp
from tenant_routes import tenant_bp
from payment_routes import payment_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(property_bp)
    app.register_blueprint(tenant_bp)
    app.register_blueprint(payment_bp)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)