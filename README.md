# Pseudo Booqable

A modern, full-stack web application designed for rental business management. Built with Flask, SQLAlchemy, TailwindCSS, and Alpine.js, it provides a seamless interface for managing products, tracking inventory availability, handling customer orders, and processing payments.

## Features

- **Product Management:** Create, edit, and organize rental products with custom pricing tiers (hourly, daily, weekly, monthly).
- **Inventory & Availability Tracking:** Real-time checking of equipment availability down to the hour.
- **Calendar View:** A centralized, global 14-day calendar to visually monitor product availability, booked stock, and specific active orders.
- **Order Processing:** Draft, confirm, pick up, and return lifecycle for rental orders.
- **Invoicing & Payments:** Generate printable invoices and record partial/full payments.
- **Customer Management:** Keep track of customer contact information and order history.
- **Settings:** Configure global application settings such as business name and address for invoices.

## Tech Stack

- **Backend:** Python 3, Flask, SQLAlchemy (ORM), Flask-Login (Authentication), Flask-WTF (Forms), Alembic (Migrations).
- **Database:** SQLite (default for development), easily adaptable to PostgreSQL.
- **Frontend:** TailwindCSS, Vanilla JS/Alpine.js for interactivity.
- **Templating:** Jinja2

## Setup & Installation

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd pseudo-booqable
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   Create a `.env` file in the root directory:
   ```env
   FLASK_APP=app:create_app
   FLASK_ENV=development
   SECRET_KEY=your_super_secret_key_here
   DATABASE_URL=sqlite:///booqable.db
   ```

5. **Initialize the database:**
   ```bash
   flask db upgrade
   ```

6. **Seed the database (Optional):**
   ```bash
   python seed.py
   ```

7. **Run the application:**
   ```bash
   flask run
   ```
   Access the app at `http://localhost:5000`.

## Testing

Run unit tests using pytest:
```bash
pytest tests/
```

## Security

- Passwords are hashed using Werkzeug's `scrypt`.
- CSRF protection enabled on all forms via `Flask-WTF`.
- Input validation on client side (HTML5) and server side (WTForms).
- Jinja2 auto-escaping active to prevent XSS.

## License

This project is licensed under the MIT License.
