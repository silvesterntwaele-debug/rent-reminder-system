from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User
from extensions import bcrypt

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    full_name = data.get("fullName", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not full_name or not email or not password:
        return jsonify({"error": "fullName, email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if User.query.filter_by(Email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(FullName=full_name, Email=email, PasswordHash=hashed, Role="landlord")
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.UserID))
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(Email=email).first()
    if not user or not bcrypt.check_password_hash(user.PasswordHash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.UserID))
    return jsonify({"token": token, "user": user.to_dict()}), 200