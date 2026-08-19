from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Tenant, Property

tenant_bp = Blueprint("tenants", __name__, url_prefix="/api/tenants")


def _verify_property_ownership(property_id, landlord_id):
    return Property.query.filter_by(PropertyID=property_id, LandlordID=landlord_id).first()


@tenant_bp.route("", methods=["GET"])
@jwt_required()
def list_tenants():
    landlord_id = get_jwt_identity()
    search = request.args.get("search", "").strip().lower()

    query = Tenant.query.join(Property).filter(Property.LandlordID == landlord_id)
    if search:
        query = query.filter(Tenant.FullName.ilike(f"%{search}%"))

    tenants = query.all()
    return jsonify([t.to_dict() for t in tenants]), 200


@tenant_bp.route("", methods=["POST"])
@jwt_required()
def create_tenant():
    landlord_id = get_jwt_identity()
    data = request.get_json() or {}

    property_id = data.get("propertyId")
    full_name = data.get("fullName", "").strip()
    email = data.get("email", "").strip()
    monthly_rent = data.get("monthlyRent")
    rent_due_day = data.get("rentDueDay", 1)

    if not property_id or not full_name or not email or monthly_rent is None:
        return jsonify({"error": "propertyId, fullName, email, monthlyRent are required"}), 400
    if not _verify_property_ownership(property_id, landlord_id):
        return jsonify({"error": "Property not found"}), 404
    if not (1 <= int(rent_due_day) <= 28):
        return jsonify({"error": "rentDueDay must be between 1 and 28"}), 400

    lease_start = data.get("leaseStart")
    tenant = Tenant(
        PropertyID=property_id,
        FullName=full_name,
        Email=email,
        Phone=data.get("phone"),
        UnitNumber=data.get("unitNumber"),
        MonthlyRent=monthly_rent,
        RentDueDay=rent_due_day,
        LeaseStart=datetime.strptime(lease_start, "%Y-%m-%d").date() if lease_start else None,
    )
    db.session.add(tenant)
    db.session.commit()
    return jsonify(tenant.to_dict()), 201


@tenant_bp.route("/<int:tenant_id>", methods=["PUT"])
@jwt_required()
def update_tenant(tenant_id):
    landlord_id = get_jwt_identity()
    tenant = Tenant.query.join(Property).filter(
        Tenant.TenantID == tenant_id, Property.LandlordID == landlord_id
    ).first()
    if not tenant:
        return jsonify({"error": "Tenant not found"}), 404

    data = request.get_json() or {}
    for field, attr in [
        ("fullName", "FullName"), ("email", "Email"), ("phone", "Phone"),
        ("unitNumber", "UnitNumber"), ("monthlyRent", "MonthlyRent"),
        ("rentDueDay", "RentDueDay"), ("isActive", "IsActive"),
    ]:
        if field in data:
            setattr(tenant, attr, data[field])

    db.session.commit()
    return jsonify(tenant.to_dict()), 200


@tenant_bp.route("/<int:tenant_id>", methods=["DELETE"])
@jwt_required()
def delete_tenant(tenant_id):
    landlord_id = get_jwt_identity()
    tenant = Tenant.query.join(Property).filter(
        Tenant.TenantID == tenant_id, Property.LandlordID == landlord_id
    ).first()
    if not tenant:
        return jsonify({"error": "Tenant not found"}), 404
    db.session.delete(tenant)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200