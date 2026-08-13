## Phase 1 — Project Scaffolding & Auth

### Overview
Set up the initial project structure for **Pseudo Booqable** (Rental Booking System), configure the database with SQLAlchemy 2.x and Flask-Migrate, establish user authentication via Flask-Login & Flask-WTF, compile TailwindCSS 3.3, and create a protected dashboard.

---

### Tasks

- [ ] **1.1** Create the application folder structure (`app/`, `app/models/`, `app/blueprints/`, `app/services/`, `app/static/`, `app/templates/`, `tests/`)
- [ ] **1.2** Create `config.py` with `Config` class loading `SECRET_KEY`, `DATABASE_URL` from `.env` via `python-dotenv`, setting `SQLALCHEMY_TRACK_MODIFICATIONS = False` and upload file limit (`MAX_CONTENT_LENGTH = 5MB`)
- [ ] **1.3** Create `app/extensions.py` — instantiate `SQLAlchemy`, `Migrate`, and `LoginManager`
- [ ] **1.4** Create `app/__init__.py` with `create_app()` factory function:
  - Load config
  - Initialize extensions (`db.init_app`, `migrate.init_app`, `login_manager.init_app`)
  - Set `login_manager.login_view = 'auth.login'` and `login_manager.login_message_category = 'info'`
  - Register `user_loader`
  - Register blueprints (`auth`, `dashboard`, `products`, `customers`, `orders`, `invoices`)
- [ ] **1.5** Create `run.py` entry point
- [ ] **1.6** Implement all database models in `app/models/`:
  - `User` (`users` table) with password hashing methods and `UserMixin`
  - `Product` (`products` table)
  - `Customer` (`customers` table)
  - `Order` (`orders` table)
  - `OrderItem` (`order_items` table)
  - Export all models in `app/models/__init__.py`
- [ ] **1.7** Initialize and run database migrations:
  - `flask db init`
  - `flask db migrate -m "initial schema"`
  - `flask db upgrade`
- [ ] **1.8** Implement authentication blueprint (`app/blueprints/auth/`):
  - `GET /auth/login` — render login form
  - `POST /auth/login` — authenticate user, create session, redirect to dashboard or `next` URL
  - `GET /auth/register` — render registration form
  - `POST /auth/register` — create new user, flash message, redirect to login
  - `GET /auth/logout` — logout user, redirect to login
- [ ] **1.9** Create `LoginForm` and `RegisterForm` in `app/blueprints/auth/forms.py` with Flask-WTF validators
- [ ] **1.10** Setup TailwindCSS 3.3:
  - `package.json` with `css:build` and `css:watch` scripts
  - `tailwind.config.js` with content paths for templates and static JS
  - `app/static/css/input.css` source file and build compiled `output.css`
- [ ] **1.11** Create templates:
  - Master layout `app/templates/base.html`
  - Partials: `components/_navbar.html`, `components/_sidebar.html`, `components/_flash_messages.html`
  - Auth pages: `auth/login.html`, `auth/register.html`
  - Dashboard: `dashboard/index.html` (protected by `@login_required`)
- [ ] **1.12** Add automated test suite in `tests/`:
  - `tests/conftest.py` with test app, client, and in-memory SQLite fixture
  - `tests/test_auth.py` testing registration, login, logout, password hashing, and access control

---

### Acceptance Criteria
- [x] Application starts cleanly with `flask run` / `python run.py`.
- [x] Visiting `/` while logged out redirects to `/auth/login`.
- [x] A user can register a new account, login, see the protected dashboard, and logout.
- [x] Responsive sidebar navigation and navbar are styled with TailwindCSS.
- [x] All database tables (`users`, `products`, `customers`, `orders`, `order_items`) exist and are tracked via Alembic migrations.
- [x] Test suite passes with `pytest`.
