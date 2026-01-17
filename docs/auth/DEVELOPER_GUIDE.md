# 👨‍💻 Developer Guide - Authentication System

Panduan lengkap untuk developer yang ingin mengembangkan atau memodifikasi sistem authentication.

---

## 📁 File Structure

```
app/
├── models/
│   └── user_model.py          # User model & database schema
├── services/
│   └── auth_service.py        # Business logic layer
├── controllers/
│   └── auth_controller.py     # Request handlers
├── decorators/
│   ├── security.py            # @api_key_required, @internal_key_required
│   └── roles.py               # @admin_required, @premium_required
└── routes/
    └── auth_routes.py         # Route definitions
```

---

## 🔄 Request Flow

Berikut adalah alur request dari client sampai database:

```
1. Client Request
   └─> Flask Route (auth_routes.py)
       └─> Security Decorator (security.py / roles.py)
           └─> Controller (auth_controller.py)
               └─> Service (auth_service.py)
                   └─> Model (user_model.py)
                       └─> Database
```

### Example: Login Request Flow

```python
# 1. Route Definition (auth_routes.py)
@auth_bp.route('/login', methods=['POST'])
def login_route():
    return login()  # Calls controller

# 2. Controller (auth_controller.py)
def login():
    data = request.get_json()
    user = AuthService.authenticate_user(  # Calls service
        data.get('email'),
        data.get('password')
    )
    if user:
        return jsonify({"status": "success", "data": user.to_dict()})

# 3. Service (auth_service.py)
class AuthService:
    @staticmethod
    def authenticate_user(email, password):
        user = User.query.filter_by(email=email).first()  # Calls model
        if user and user.check_password(password):
            return user
        return None

# 4. Model (user_model.py)
class User(db.Model):
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

---

## 🎨 Adding New Features

### 1. Add New Field to User Model

**Step 1:** Update model

```python
# app/models/user_model.py
class User(db.Model):
    # ... existing fields ...

    # New field
    phone_number = db.Column(db.String(20), nullable=True)
```

**Step 2:** Create migration

```bash
flask db migrate -m "Add phone number field"
flask db upgrade
```

**Step 3:** Update `to_dict()` method

```python
def to_dict(self, include_api_key=False):
    data = {
        # ... existing fields ...
        "phone_number": self.phone_number,
    }
    return data
```

### 2. Add New Endpoint

**Step 1:** Create controller function

```python
# app/controllers/auth_controller.py
@api_key_required
def update_phone():
    data = request.get_json()
    phone = data.get('phone_number')

    g.current_user.phone_number = phone
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Phone number updated"
    }), 200
```

**Step 2:** Register route

```python
# app/routes/auth_routes.py
auth_bp.route('/update-phone', methods=['POST'])(update_phone)
```

**Step 3:** Test endpoint

```bash
curl -X POST http://localhost:5000/api/v1/auth/update-phone \
  -H "X-API-KEY: your-key" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

### 3. Add New Decorator

**Example:** Create `@verified_email_required` decorator

```python
# app/decorators/security.py
def verified_email_required(f):
    @wraps(f)
    @api_key_required  # Stack with existing decorator
    def decorated_function(*args, **kwargs):
        if not g.current_user.email_verified:
            return jsonify({
                "status": "error",
                "message": "Email verification required"
            }), 403
        return f(*args, **kwargs)
    return decorated_function
```

**Usage:**

```python
@app.route('/premium-feature')
@verified_email_required
def premium_feature():
    return jsonify({"status": "success"})
```

---

## 🔒 Security Best Practices

### 1. Password Handling

```python
# ✅ Good: Always hash passwords
user.set_password(plain_password)  # Uses bcrypt internally

# ❌ Bad: Never store plain passwords
user.password = plain_password  # NEVER do this
```

### 2. API Key Visibility

```python
# ✅ Good: Only include API key when needed
user.to_dict(include_api_key=True)  # Only on login/register

# ❌ Bad: Always including API key
user.to_dict()  # Should NOT include API key by default
```

### 3. Input Validation

```python
# ✅ Good: Validate all inputs
def register():
    data = request.get_json()

    if not data or not data.get('email'):
        return jsonify({"error": "Email required"}), 400

    # Validate email format
    try:
        validate_email(data['email'])
    except EmailNotValidError:
        return jsonify({"error": "Invalid email"}), 400
```

### 4. Error Messages

```python
# ✅ Good: Generic error messages
return jsonify({"error": "Invalid credentials"}), 401

# ❌ Bad: Revealing too much info
return jsonify({"error": "Email not found"}), 404  # Reveals email exists
return jsonify({"error": "Wrong password"}), 401  # Confirms email exists
```

### 5. Rate Limiting (TODO)

```python
# Future implementation
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/login')
@limiter.limit("5 per minute")
def login():
    # Login logic
    pass
```

---

## 🧪 Testing

### Unit Tests

```python
# tests/test_auth.py
import unittest
from app import create_app, db
from app.models.user_model import User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_registration(self):
        response = self.client.post('/api/v1/auth/register', json={
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')

    def test_login(self):
        # First register
        self.client.post('/api/v1/auth/register', json={
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        })

        # Then login
        response = self.client.post('/api/v1/auth/login', json={
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('api_key', data['data'])
```

### Integration Tests

```python
def test_brute_force_protection(self):
    # Register user
    self.client.post('/api/v1/auth/register', json={
        'email': 'test@example.com',
        'password': 'SecurePass123!'
    })

    # Try wrong password 5 times
    for i in range(5):
        response = self.client.post('/api/v1/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPassword'
        })

    # 6th attempt should be locked
    response = self.client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'WrongPassword'
    })
    self.assertEqual(response.status_code, 403)
    data = response.get_json()
    self.assertIn('locked', data['message'].lower())
```

### Manual Testing

```bash
# Use test_quick.py
python test_quick.py

# Or test_auth.py for comprehensive tests
python test_auth.py
```

---

## 🐛 Debugging

### Enable Debug Mode

```python
# config/config.py
DEBUG = True  # Enable detailed error messages
```

### View Logs

```python
# Add logging to any function
import logging
logger = logging.getLogger(__name__)

def login():
    logger.info(f"Login attempt for email: {email}")
    # ... rest of code
```

### Database Debugging

```python
# View SQL queries
app.config['SQLALCHEMY_ECHO'] = True

# Check current user in decorator
@api_key_required
def some_endpoint():
    print(f"Current user: {g.current_user.email}")
    print(f"Role: {g.current_user.role}")
```

### Common Issues

**Issue: API key not working**

```python
# Check if API key is being sent
print(f"Headers: {request.headers}")
print(f"API Key: {request.headers.get('X-API-KEY')}")
```

**Issue: Password reset token invalid**

```python
# Check token expiration
user = User.query.filter_by(reset_token=token).first()
print(f"Token: {user.reset_token}")
print(f"Expires: {user.reset_token_expires}")
print(f"Now: {datetime.utcnow()}")
```

---

## 📊 Performance Optimization

### Database Queries

```python
# ❌ Bad: N+1 query problem
users = User.query.all()
for user in users:
    print(user.role)  # Each iteration hits DB

# ✅ Good: Load everything at once
users = User.query.options(
    db.joinedload('related_table')
).all()
```

### Caching (Future)

```python
# Cache frequently accessed data
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300, key_prefix='user_by_api_key')
def get_user_by_api_key(api_key):
    return User.query.filter_by(api_key=api_key).first()
```

### Indexing

```python
# Add indexes for frequently queried fields
class User(db.Model):
    email = db.Column(db.String(120), unique=True, index=True)
    api_key = db.Column(db.String(64), unique=True, index=True)
```

---

## 🚀 Deployment Checklist

### Before Production

- [ ] **Security**

  - [ ] Set `DEBUG = False`
  - [ ] Use strong `SECRET_KEY`
  - [ ] Enable HTTPS only
  - [ ] Remove dev-only endpoints
  - [ ] Enable rate limiting

- [ ] **Email**

  - [ ] Configure SMTP settings
  - [ ] Test password reset emails
  - [ ] Setup email templates

- [ ] **Database**

  - [ ] Use PostgreSQL (not SQLite)
  - [ ] Enable connection pooling
  - [ ] Setup automated backups
  - [ ] Run all migrations

- [ ] **Monitoring**

  - [ ] Setup error tracking (Sentry)
  - [ ] Enable access logs
  - [ ] Setup alerts for failed logins
  - [ ] Monitor API usage

- [ ] **Testing**
  - [ ] Run full test suite
  - [ ] Load testing
  - [ ] Security audit
  - [ ] Penetration testing

### Environment Variables

```bash
# .env.production
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DEBUG=False
INTERNAL_SERVICE_KEY=<another-strong-key>

# Email settings
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=<app-password>
```

---

## 📝 Code Style Guide

### Naming Conventions

```python
# Functions: snake_case
def authenticate_user():
    pass

# Classes: PascalCase
class AuthService:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_LOGIN_ATTEMPTS = 5

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

### Documentation

```python
def complex_function(param1, param2):
    """
    Short description of function.

    Longer description if needed, explaining the purpose,
    algorithm, or important notes.

    Args:
        param1 (str): Description of param1
        param2 (int): Description of param2

    Returns:
        dict: Description of return value

    Raises:
        ValueError: When param1 is invalid
        KeyError: When param2 not found

    Example:
        >>> result = complex_function("test", 123)
        >>> print(result)
        {'status': 'success'}
    """
    pass
```

### Import Organization

```python
# Standard library
import os
import sys
from datetime import datetime

# Third-party packages
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash

# Local imports
from app.models import User
from app.services import AuthService
```

---

## 🤝 Contributing Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/email-verification
```

### 2. Make Changes

- Write code
- Add tests
- Update documentation

### 3. Test Locally

```bash
# Run tests
python -m pytest

# Check code style
flake8 app/

# Run the app
python main.py
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: Add email verification feature"
```

### 5. Push & Create PR

```bash
git push origin feature/email-verification
# Create Pull Request on GitHub
```

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example:**

```
feat: Add email verification for new users

- Add email_verified field to User model
- Create verification token generation
- Add send_verification_email function
- Update registration to send verification email

Closes #123
```

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)
- [REST API Best Practices](https://restfulapi.net/)

---

## 💡 Tips & Tricks

### Quick Commands

```bash
# Create new migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# Open Flask shell
flask shell

# Create admin user
python create_admin.py
```

### Flask Shell Tips

```python
# Access database in shell
$ flask shell
>>> from app.models import User
>>> users = User.query.all()
>>> print(users[0].email)

# Quick user creation
>>> user = User(email='test@example.com')
>>> user.set_password('password123')
>>> user.generate_api_key()
>>> db.session.add(user)
>>> db.session.commit()
```

### VS Code Snippets

Add to `.vscode/settings.json`:

```json
{
  "python.snippets": {
    "Flask Route": {
      "prefix": "froute",
      "body": [
        "@app.route('/${1:endpoint}', methods=['${2:GET}'])",
        "def ${3:function_name}():",
        "    ${4:pass}"
      ]
    }
  }
}
```

---

Happy Coding! 🚀
