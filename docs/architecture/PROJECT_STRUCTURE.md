# 🏗️ Project Structure

Dokumentasi lengkap tentang struktur folder dan file dalam project.

---

## 📁 Root Structure

```
Backend/
├── app/                    # Main application package
├── config/                 # Configuration files
├── migrations/             # Database migrations (Alembic)
├── instance/              # Instance-specific files (gitignored)
├── docs/                  # Documentation
├── tests/                 # Test files (TODO)
├── venv/                  # Virtual environment (gitignored)
├── main.py               # Application entry point
├── create_admin.py       # Admin user creation script
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (gitignored)
├── .gitignore           # Git ignore rules
└── README.md            # Project README
```

---

## 📦 App Package Structure

```
app/
├── __init__.py           # App factory & initialization
├── extensions.py         # Flask extensions (db, migrate, etc.)
│
├── models/              # Database models
│   ├── __init__.py
│   └── user_model.py    # User model
│
├── services/            # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py  # Auth business logic
│   └── admin/
│       ├── __init__.py
│       └── admin_service.py
│
├── controllers/         # Request handlers
│   ├── __init__.py
│   ├── auth_controller.py
│   └── admin/
│       ├── __init__.py
│       └── admin_controller.py
│
├── routes/             # Route definitions
│   ├── __init__.py
│   ├── auth_routes.py
│   └── admin/
│       ├── __init__.py
│       └── admin_routes.py
│
└── decorators/         # Custom decorators
    ├── __init__.py
    ├── security.py     # @api_key_required
    └── roles.py        # @admin_required, @premium_required
```

---

## 📝 File Descriptions

### Root Level

#### main.py

Entry point untuk menjalankan aplikasi.

```python
from app import create_app
from config.config import Config

app = create_app()

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
```

#### create_admin.py

Script untuk membuat admin user pertama.

```python
from app import create_app, db
from app.models.user_model import User

# Creates admin user with email and password
```

#### requirements.txt

Daftar semua Python dependencies.

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
# ... etc
```

---

### Configuration

#### config/config.py

Konfigurasi aplikasi dari environment variables.

```python
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')
    DEBUG = os.getenv('DEBUG')
    # ... etc
```

**Environment Variables (.env):**

```bash
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host/db
DEBUG=True
PORT=5000
HOST=127.0.0.1
INTERNAL_SERVICE_KEY=internal-key
```

---

### App Package

#### app/**init**.py

Application factory pattern.

```python
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    # ...

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

    return app
```

**Benefits:**

- Multiple app instances
- Easy testing
- Clean separation

#### app/extensions.py

Flask extensions initialization.

```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cors = CORS()
```

---

### Models Layer

#### app/models/user_model.py

User database model & methods.

**Responsibilities:**

- Define database schema
- Password hashing/verification
- API key generation
- Security helpers (lock, quota, etc.)

**Key Methods:**

```python
class User(UserMixin, db.Model):
    def set_password(password)           # Hash password
    def check_password(password)         # Verify password
    def generate_api_key()               # Create new API key
    def is_account_locked()              # Check lock status
    def increment_failed_login()         # Track failed attempts
    def has_quota_remaining()            # Check usage quota
```

---

### Services Layer

#### app/services/auth_service.py

Authentication business logic.

**Responsibilities:**

- User registration
- User authentication
- Password reset
- API key regeneration
- Business rules & validations

**Key Methods:**

```python
class AuthService:
    @staticmethod
    def register_user(email, password)

    @staticmethod
    def authenticate_user(email, password)

    @staticmethod
    def request_password_reset(email)

    @staticmethod
    def reset_password(token, new_password)

    @staticmethod
    def regenerate_api_key(user, expires_in_days)
```

**Why Service Layer:**

- Reusable business logic
- Testable without HTTP
- Clear separation of concerns

---

### Controllers Layer

#### app/controllers/auth_controller.py

HTTP request handlers.

**Responsibilities:**

- Parse request data
- Validate inputs
- Call service methods
- Format responses
- Handle errors

**Example:**

```python
def register():
    data = request.get_json()

    # Input validation
    if not data or not data.get('email'):
        return jsonify({"error": "Email required"}), 400

    try:
        # Call service
        user = AuthService.register_user(data['email'], data['password'])

        # Format response
        return jsonify({
            "status": "success",
            "user": user.to_dict(include_api_key=True)
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
```

---

### Routes Layer

#### app/routes/auth_routes.py

URL route definitions.

```python
from flask import Blueprint
from app.controllers.auth_controller import register, login, logout

auth_bp = Blueprint('auth', __name__)

auth_bp.route('/register', methods=['POST'])(register)
auth_bp.route('/login', methods=['POST'])(login)
auth_bp.route('/logout', methods=['POST'])(logout)
```

**Blueprint Benefits:**

- Modular routing
- Easy to organize
- Can be versioned

---

### Decorators Layer

#### app/decorators/security.py

Authentication decorators.

```python
@api_key_required
def protected_endpoint():
    # g.current_user is available here
    return jsonify({"user": g.current_user.email})
```

**Key Decorators:**

- `@api_key_required` - Validate API key
- `@internal_key_required` - Internal service auth

#### app/decorators/roles.py

Authorization decorators.

```python
@admin_required
def admin_only():
    # Only admins can access
    pass

@premium_required
def premium_feature():
    # Premium & admin can access
    pass
```

---

## 🔄 Request Flow Example

### Registration Request

```
1. HTTP POST /api/v1/auth/register
   ↓
2. Flask Router → auth_routes.py
   ↓
3. Controller → auth_controller.register()
   ↓
4. Service → AuthService.register_user()
   ↓
5. Model → User.set_password(), User.generate_api_key()
   ↓
6. Database → INSERT INTO user
   ↓
7. Response ← JSON {"status": "success", "user": {...}}
```

### Protected Endpoint Request

```
1. HTTP GET /api/v1/auth/me
   Headers: X-API-KEY: abc123...
   ↓
2. Flask Router → auth_routes.py
   ↓
3. Decorator → @api_key_required validates key
   ↓
4. Controller → auth_controller.get_current_user()
   ↓
5. Response ← JSON {"user": {...}}
```

---

## 📚 Documentation Structure

```
docs/
├── README.md                    # Documentation index
├── CONTRIBUTING.md              # Contribution guidelines
├── CODE_STYLE.md               # Code style guide
├── TESTING.md                  # Testing guide
│
├── auth/                       # Auth documentation
│   ├── README.md              # Auth overview
│   ├── API.md                 # API reference
│   ├── DATABASE.md            # Database schema
│   ├── DEVELOPER_GUIDE.md     # Developer guide
│   └── SECURITY.md            # Security features
│
└── architecture/              # Architecture docs
    ├── PROJECT_STRUCTURE.md   # This file
    ├── TECH_STACK.md          # Technologies used
    └── PATTERNS.md            # Design patterns
```

---

## 🗄️ Database Migrations

```
migrations/
├── alembic.ini                # Alembic configuration
├── env.py                     # Migration environment
├── script.py.mako            # Migration template
└── versions/                  # Migration files
    ├── 3042d6f8337d_initial_v2_structure.py
    └── d2c7c8dd8243_add_security_features.py
```

**Managing Migrations:**

```bash
# Create new migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# View migration history
flask db history
```

---

## 🧪 Testing Structure (TODO)

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_auth.py            # Auth tests
├── test_models.py          # Model tests
├── test_services.py        # Service tests
└── test_api.py             # API integration tests
```

---

## 📦 Instance Folder

```
instance/
└── app.db                   # SQLite database (development)
```

**Purpose:**

- Development database
- User-uploaded files
- Local configuration overrides

**Note:** This folder is gitignored.

---

## 🔧 Configuration Files

### .gitignore

```
venv/
__pycache__/
*.pyc
.env
instance/
*.db
.DS_Store
```

### .env (Example)

```bash
# Flask
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
HOST=127.0.0.1
PORT=5000

# Database
DATABASE_URL=sqlite:///instance/app.db

# Security
INTERNAL_SERVICE_KEY=internal-key-123

# Email (TODO)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

## 🎨 Design Patterns Used

### 1. Application Factory Pattern

```python
# app/__init__.py
def create_app(config_class=Config):
    app = Flask(__name__)
    # Initialize app
    return app
```

### 2. Blueprint Pattern

```python
# Modular routing
auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__)
```

### 3. Decorator Pattern

```python
@api_key_required
@admin_required
def protected_route():
    pass
```

### 4. Service Layer Pattern

```python
# Separate business logic from HTTP
class AuthService:
    @staticmethod
    def register_user(email, password):
        # Business logic here
        pass
```

### 5. Repository Pattern (via ORM)

```python
# Data access through SQLAlchemy
user = User.query.filter_by(email=email).first()
```

---

## 📊 Directory Organization Rules

### Naming Conventions

- **Folders:** `lowercase_snake_case`
- **Python files:** `lowercase_snake_case.py`
- **Classes:** `PascalCase`
- **Functions:** `snake_case`

### File Organization

- Max 500 lines per file
- One class per file (models)
- Group related functions
- Clear module boundaries

### Import Organization

```python
# Standard library
import os
from datetime import datetime

# Third-party
from flask import Flask, request
from sqlalchemy import Column

# Local
from app.models import User
from app.services import AuthService
```

---

## 🚀 Scalability Considerations

### Current Structure

```
Single App Instance
    ↓
All Components in One Process
    ↓
Single Database
```

### Future: Microservices (if needed)

```
API Gateway
    ├── Auth Service (this app)
    ├── Image Processing Service
    ├── Storage Service
    └── Analytics Service
```

### Future: Modular Monolith

```
app/
├── auth/           # Auth module (isolated)
├── image/          # Image processing module
├── storage/        # Storage module
└── shared/         # Shared utilities
```

---

## 📝 File Naming Conventions

| Type       | Pattern           | Example              |
| ---------- | ----------------- | -------------------- |
| Model      | `*_model.py`      | `user_model.py`      |
| Service    | `*_service.py`    | `auth_service.py`    |
| Controller | `*_controller.py` | `auth_controller.py` |
| Routes     | `*_routes.py`     | `auth_routes.py`     |
| Test       | `test_*.py`       | `test_auth.py`       |
| Config     | `*.py`            | `config.py`          |

---

## 🔍 Finding Your Way

**Want to:**

- Add new endpoint? → `routes/` → `controllers/`
- Add business logic? → `services/`
- Change database? → `models/`
- Add security? → `decorators/`
- Configure app? → `config/`
- See API docs? → `docs/auth/API.md`

---

## 🤝 Contributing

When adding new features:

1. Create model (if needed) in `models/`
2. Write business logic in `services/`
3. Create controller in `controllers/`
4. Register routes in `routes/`
5. Add tests in `tests/`
6. Update documentation in `docs/`

---

**Keep it clean, keep it organized! 🎯**
