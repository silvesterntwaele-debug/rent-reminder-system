# Rent Reminder System

A landlord/property management tool for tracking properties, tenants, rent payments, and overdue accounts — built to solve a real problem: manually chasing tenants for rent every month.

Built with **Python (Flask)**, **vanilla JavaScript**, and **SQL Server**, using JWT authentication and a REST API architecture.

## Why this project

Landlords and small property managers often track rent in spreadsheets or WhatsApp reminders, which doesn't scale past a handful of tenants and makes it easy to lose track of who's paid. This system centralizes properties, tenants, and payments in one place, and automatically flags overdue rent based on due dates — no manual bookkeeping required.

## Features (Version 1 — MVP, complete)

- Landlord registration and login (JWT-based auth, bcrypt password hashing)
- Dashboard showing property/tenant counts, overdue totals, and upcoming due payments
- Add / delete properties
- Add / delete tenants, with search
- Record rent payments and mark them as paid
- Automatic overdue detection — status is recalculated live against today's date, no manual flagging

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Bcrypt |
| Database | SQL Server (via pyodbc) |
| Frontend | HTML, CSS, vanilla JavaScript (fetch API, no framework) |
| Auth | JWT tokens, bcrypt-hashed passwords |

## Project structure
rent-reminder-system/
├── app.py                # Flask app factory + entry point
├── config.py               # DB connection string, JWT settings
├── models.py                 # SQLAlchemy models: User, Property, Tenant, Payment
├── extensions.py               # Shared bcrypt/jwt instances
├── schema.sql                    # Raw SQL Server DDL
├── auth_routes.py                  # Register / login endpoints
├── property_routes.py                # Property CRUD
├── tenant_routes.py                    # Tenant CRUD + search
├── payment_routes.py                     # Payment CRUD, mark-paid, dashboard summary
├── index.html                              # Login / register page
├── dashboard.html                            # Main app UI
├── style.css
├── api.js                                      # Central fetch wrapper + API calls
├── auth.js
├── dashboard.js
├── requirements.txt
├── .env.example
└── screenshots/                                    # App screenshots

## Setup and installation

### 1. Database
Open SSMS and run:
```sql
CREATE DATABASE RentReminderDB;

Then run schema.sql against it, or skip this — the app will create tables automatically on first run.
2. Environment variables
Copy .env.example to .env and fill in your SQL Server details and a JWT secret key.
3. Backend
pip install -r requirements.txt
python app.py
Runs at http://127.0.0.1:5000. Requires the ODBC Driver 17 (or 18) for SQL Server installed locally.
4. Frontend
In a second terminal:
python -m http.server 8080
Then open http://localhost:8080/index.html in your browser.
API overview
Method
Endpoint
Description
POST
/api/auth/register
Create a landlord account
POST
/api/auth/login
Authenticate, receive JWT
GET / POST
/api/properties
List / create properties
DELETE
/api/properties/<id>
Delete a property
GET / POST
/api/tenants
List (with ?search=) / create tenants
PUT / DELETE
/api/tenants/<id>
Update / delete a tenant
GET / POST
/api/payments
List (with ?status=) / create payments
POST
/api/payments/<id>/mark-paid
Mark a payment paid
GET
/api/payments/dashboard
Aggregated dashboard stats
All endpoints except register/login require a Authorization: Bearer <token> header.
Screenshots
See the screenshots/ folder for the login page, dashboard, and payment tracking views.

Author
Thato Silvester Ntwaele
