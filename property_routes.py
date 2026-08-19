from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Property

property_bp = Blueprint("properties", __name__, url_prefix="/api/properties")


@property_bp.route("", methods=["GET"])
@jwt_required()
def list_properties():
    landlord_id = get_jwt_identity()
    props = Property.query.filter_by(LandlordID=landlord_id).all()
    return jsonify([p.to_dict() for p in props]), 200


@property_bp.route("", methods=["POST"])
@jwt_required()
def create_property():
    landlord_id = get_jwt_identity()
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    address = data.get("address", "").strip()

    if not name or not address:
        return jsonify({"error": "name and address are required"}), 400

    prop = Property(
        LandlordID=landlord_id,
        Name=name,
        AddressLine=address,
        City=data.get("city"),
        Province=data.get("province"),
    )
    db.session.add(prop)
    db.session.commit()
    return jsonify(prop.to_dict()), 201


@property_bp.route("/<int:property_id>", methods=["DELETE"])
@jwt_required()
def delete_property(property_id):
    landlord_id = get_jwt_identity()
    prop = Property.query.filter_by(PropertyID=property_id, LandlordID=landlord_id).first()
    if not prop:
        return jsonify({"error": "Property not found"}), 404
    db.session.delete(prop)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200