from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Payment, Tenant, Property

payment_bp = Blueprint("payments", __name__, url_prefix="/api/payments")


def _owned_tenant(tenant_id, landlord_id):
    return Tenant.query.join(Property).filter(
        Tenant.TenantID == tenant_id, Property.LandlordID == landlord_id
    ).first()


def _refresh_all_statuses(landlord_id):
    """Flip any unpaid payment whose due date has passed into 'overdue'."""
    payments = Payment.query.join(Tenant).join(Property).filter(
        Property.LandlordID == landlord_id
    ).all()
    changed = False
    for p in payments:
        old_status = p.Status
        p.refresh_status()
        if p.Status != old_status:
            changed = True
    if changed:
        db.session.commit()
    return payments


@payment_bp.route("", methods=["GET"])
@jwt_required()
def list_payments():
    landlord_id = get_jwt_identity()
    status = request.args.get("status")  # unpaid | paid | overdue | partial

    payments = _refresh_all_statuses(landlord_id)
    if status:
        payments = [p for p in payments if p.Status == status]

    payments.sort(key=lambda p: p.DueDate)
    return jsonify([p.to_dict() for p in payments]), 200


@payment_bp.route("", methods=["POST"])
@jwt_required()
def create_payment():
    landlord_id = get_jwt_identity()
    data = request.get_json() or {}

    tenant_id = data.get("tenantId")
    due_date = data.get("dueDate")
    amount_due = data.get("amountDue")

    if not tenant_id or not due_date or amount_due is None:
        return jsonify({"error": "tenantId, dueDate, amountDue are required"}), 400

    tenant = _owned_tenant(tenant_id, landlord_id)
    if not tenant:
        return jsonify({"error": "Tenant not found"}), 404

    payment = Payment(
        TenantID=tenant_id,
        AmountDue=amount_due,
        DueDate=datetime.strptime(due_date, "%Y-%m-%d").date(),
        AmountPaid=0,
    )
    payment.refresh_status()
    db.session.add(payment)
    db.session.commit()
    return jsonify(payment.to_dict()), 201


@payment_bp.route("/<int:payment_id>/mark-paid", methods=["POST"])
@jwt_required()
def mark_paid(payment_id):
    landlord_id = get_jwt_identity()
    payment = Payment.query.join(Tenant).join(Property).filter(
        Payment.PaymentID == payment_id, Property.LandlordID == landlord_id
    ).first()
    if not payment:
        return jsonify({"error": "Payment not found"}), 404

    data = request.get_json() or {}
    amount = data.get("amountPaid", float(payment.AmountDue))
    payment.AmountPaid = amount
    payment.PaidDate = date.today()
    payment.refresh_status()
    db.session.commit()
    return jsonify(payment.to_dict()), 200


@payment_bp.route("/<int:payment_id>", methods=["DELETE"])
@jwt_required()
def delete_payment(payment_id):
    landlord_id = get_jwt_identity()
    payment = Payment.query.join(Tenant).join(Property).filter(
        Payment.PaymentID == payment_id, Property.LandlordID == landlord_id
    ).first()
    if not payment:
        return jsonify({"error": "Payment not found"}), 404
    db.session.delete(payment)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200


@payment_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard_summary():
    landlord_id = get_jwt_identity()
    payments = _refresh_all_statuses(landlord_id)

    total_properties = Property.query.filter_by(LandlordID=landlord_id).count()
    total_tenants = Tenant.query.join(Property).filter(Property.LandlordID == landlord_id).count()

    overdue = [p for p in payments if p.Status == "overdue"]
    unpaid = [p for p in payments if p.Status in ("unpaid", "partial")]
    paid_this_run = [p for p in payments if p.Status == "paid"]

    upcoming_7_days = [
        p for p in payments
        if p.Status in ("unpaid", "partial") and 0 <= (p.DueDate - date.today()).days <= 7
    ]

    return jsonify({
        "totalProperties": total_properties,
        "totalTenants": total_tenants,
        "totalOverdue": len(overdue),
        "totalOverdueAmount": sum(float(p.AmountDue) - float(p.AmountPaid) for p in overdue),
        "totalUnpaid": len(unpaid),
        "totalPaid": len(paid_this_run),
        "upcomingDue": [p.to_dict() for p in sorted(upcoming_7_days, key=lambda p: p.DueDate)],
        "overduePayments": [p.to_dict() for p in sorted(overdue, key=lambda p: p.DueDate)],
    }), 200