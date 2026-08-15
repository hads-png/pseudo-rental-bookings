# Pseudo Booqable — Rental Booking System

A robust, full-stack rental management web application inspired by Booqable. Built with Python, Flask, SQLAlchemy, MySQL, and styled with TailwindCSS.

## Project Overview

Pseudo Booqable is designed for businesses that rent out physical products (e.g., camera gear, party supplies, power tools). It provides a unified administration dashboard to:
- **Manage Inventory:** Add products, set daily rates, and track total available stock.
- **Manage Customers:** Maintain a CRM of clients and view their rental history.
- **Process Bookings:** Create orders tying customers to products over specific date ranges.
- **Availability Engine:** Automatically prevents overbooking by calculating available stock based on existing overlapping orders.
- **Invoicing & Payments:** Generate print-ready invoices and manually record customer payments.
- **Dashboard Analytics:** View real-time metrics, order status breakdowns, top rented products, and 6-month revenue charts.

## Tech Stack
- **Backend:** Python 3.12, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database:** MySQL 8.x
- **Frontend:** TailwindCSS 3.3, Jinja2 Templates, Vanilla JavaScript, Chart.js
- **Testing:** Pytest

---

## Local Development Setup

Follow these instructions to run the project locally.

### 1. Prerequisites
- Python 3.12+
- Node.js & npm (for TailwindCSS)
- MySQL Server (running locally)

### 2. Database Configuration
Log into your MySQL server and create an empty database:
```sql
CREATE DATABASE pseudo_booqable CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Environment Variables
Create a `.env` file in the root directory (do not commit this file) with the following content:
```dotenv
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-here
# Update with your MySQL username, password, and port
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/pseudo_booqable
```

### 4. Python Environment Setup
Create and activate a virtual environment, then install the dependencies:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Node.js Environment Setup
Install Node dependencies to compile the Tailwind CSS:
```bash
npm install
npm run css:build
```
*(During active UI development, you can run `npm run css:watch` to automatically rebuild CSS on save).*

### 6. Database Migrations
Initialize the database tables using Flask-Migrate:
```bash
flask db upgrade
```

### 7. Seeding the Database
To quickly populate the application with a test admin user, sample products, customers, and orders, run the seed script:
```bash
python seed.py
```
*(Note: If `seed.py` has not been implemented yet, you will need to register manually via the `/auth/register` route).*

### 8. Run the Application
Start the Flask development server:
```bash
flask run
```
Navigate to `http://127.0.0.1:5000` in your browser. 
If you used the seed script, log in with:
- **Username:** `admin`
- **Password:** `admin123`

---

## Project Structure

- `app/blueprints/` - Feature-specific route modules (auth, dashboard, products, customers, orders).
- `app/models/` - SQLAlchemy database schemas.
- `app/services/` - Core business logic (availability checks, order total calculations).
- `app/templates/` - Jinja2 HTML templates.
- `app/static/` - Compiled CSS, JavaScript, and user uploads.
- `tests/` - Comprehensive test suites spanning all modules.
