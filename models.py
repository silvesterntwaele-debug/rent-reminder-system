from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "Users"
    UserID = db.Column(db.Integer, primary_key=True)
    FullName = db.Column(db.String(150), nullable=False)
    Email = db.Column(db.String(150), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)
    Role = db.Column(db.String(20), default="landlord")
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    properties = db.relationship("Property", backref="landlord", lazy=True)

    def to_dict(self):
        return {"id": self.UserID, "fullName": self.FullName, "email": self.Email, "role": self.Role}


class Property(db.Model):
    __tablename__ = "Properties"
    PropertyID = db.Column(db.Integer, primary_key=True)
    LandlordID = db.Column(db.Integer, db.ForeignKey("Users.UserID"), nullable=False)
    Name = db.Column(db.String(150), nullable=False)
    AddressLine = db.Column(db.String(255), nullable=False)
    City = db.Column(db.String(100))
    Province = db.Column(db.String(100))
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    tenants = db.relationship("Tenant", backref="property", lazy=True)

    def to_dict(self):
        return {
            "id": self.PropertyID,
            "name": self.Name,
            "address": self.AddressLine,
            "city": self.City,
            "province": self.Province,
            "tenantCount": len(self.tenants),
        }


class Tenant(db.Model):
    __tablename__ = "Tenants"
    TenantID = db.Column(db.Integer, primary_key=True)
    PropertyID = db.Column(db.Integer, db.ForeignKey("Properties.PropertyID"), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey("Users.UserID"), nullable=True)
    FullName = db.Column(db.String(150), nullable=False)
    Email = db.Column(db.String(150), nullable=False)
    Phone = db.Column(db.String(30))
    UnitNumber = db.Column(db.String(30))
    MonthlyRent = db.Column(db.Numeric(12, 2), nullable=False)
    RentDueDay = db.Column(db.Integer, default=1)
    LeaseStart = db.Column(db.Date)
    IsActive = db.Column(db.Boolean, default=True)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    payments = db.relationship("Payment", backref="tenant", lazy=True)

    def to_dict(self):
        return {
            "id": self.TenantID,
            "propertyId": self.PropertyID,
            "propertyName": self.property.Name if self.property else None,
            "fullName": self.FullName,
            "email": self.Email,
            "phone": self.Phone,
            "unitNumber": self.UnitNumber,
            "monthlyRent": float(self.MonthlyRent),
            "rentDueDay": self.RentDueDay,
            "isActive": self.IsActive,
        }


class Payment(db.Model):
    __tablename__ = "Payments"
    PaymentID = db.Column(db.Integer, primary_key=True)
    TenantID = db.Column(db.Integer, db.ForeignKey("Tenants.TenantID"), nullable=False)
    AmountDue = db.Column(db.Numeric(12, 2), nullable=False)
    DueDate = db.Column(db.Date, nullable=False)
    AmountPaid = db.Column(db.Numeric(12, 2), default=0)
    PaidDate = db.Column(db.Date, nullable=True)
    Status = db.Column(db.String(20), default="unpaid")
    ReminderSent7Day = db.Column(db.Boolean, default=False)
    ReminderSent1Day = db.Column(db.Boolean, default=False)
    ReminderSentDueDate = db.Column(db.Boolean, default=False)
    ReminderSentOverdue = db.Column(db.Boolean, default=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    def refresh_status(self):
        """Recompute status based on today's date and amount paid."""
        if self.AmountPaid >= self.AmountDue:
            self.Status = "paid"
        elif self.AmountPaid > 0:
            self.Status = "partial"
        elif date.today() > self.DueDate:
            self.Status = "overdue"
        else:
            self.Status = "unpaid"

    def to_dict(self):
        return {
            "id": self.PaymentID,
            "tenantId": self.TenantID,
            "tenantName": self.tenant.FullName if self.tenant else None,
            "amountDue": float(self.AmountDue),
            "dueDate": self.DueDate.isoformat(),
            "amountPaid": float(self.AmountPaid),
            "paidDate": self.PaidDate.isoformat() if self.PaidDate else None,
            "status": self.Status,
        }