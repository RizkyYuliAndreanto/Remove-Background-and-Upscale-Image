# 🔐 Authentication System

## Overview

Sistem authentication yang robust dan secure untuk Background Remover & Upscale Image API, dengan fitur-fitur modern security dan user management.

---

## 🎯 Core Features

### 1. User Authentication

- ✅ Email + Password login
- ✅ Secure password hashing (bcrypt via Werkzeug)
- ✅ Session management dengan Flask-Login
- ✅ API Key authentication

### 2. Security Features

- ✅ **Brute Force Protection** - Account lock setelah 5 failed attempts
- ✅ **API Key Expiration** - Optional expiration untuk API keys
- ✅ **Password Reset** - Secure token-based password reset
- ✅ **Account Status** - Active/banned status management

### 3. Access Control

- ✅ **Role-Based Access Control (RBAC)**
  - `user` - Free tier (10 requests/month)
  - `premium` - Premium tier (1000 requests/month)
  - `admin` - Full access (unlimited)
- ✅ Decorators untuk role checking (`@admin_required`, `@premium_required`)

### 4. Usage Management

- ✅ **Usage Tracking** - Count API calls per user
- ✅ **Monthly Quota** - Auto-reset every 30 days
- ✅ **Quota Enforcement** - Prevent overuse

### 5. Activity Monitoring

- ✅ Last login tracking
- ✅ Last activity timestamp
- ✅ Failed login attempts logging

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Request                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask Routes Layer                        │
│                  (app/routes/auth_routes.py)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Security Decorators                        │
│        @api_key_required, @admin_required, etc.              │
│             (app/decorators/security.py)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Controller Layer                          │
│              (app/controllers/auth_controller.py)            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│               (app/services/auth_service.py)                 │
│         • Business logic                                     │
│         • Validation                                         │
│         • Error handling                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Model Layer                             │
│                (app/models/user_model.py)                    │
│         • Database operations                                │
│         • Data validation                                    │
│         • Helper methods                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Database                               │
│                    (PostgreSQL/SQLite)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Authentication Flow

### Registration Flow

```
1. User submits email + password
2. Validate email format & password strength
3. Check if email already exists
4. Hash password (bcrypt)
5. Generate unique API key
6. Create user in database
7. Return user data + API key
```

### Login Flow

```
1. User submits email + password
2. Check if account is locked (brute force protection)
3. Find user by email
4. Verify password hash
5. Check account status (banned/active)
6. Reset failed login counter
7. Update last_login timestamp
8. Return user data + API key
```

### API Key Authentication Flow

```
1. Client sends request with X-API-KEY header
2. Extract API key from header
3. Find user by API key
4. Check if API key is expired
5. Check if user is active
6. Update last_activity timestamp
7. Set g.current_user for request context
8. Proceed to endpoint handler
```

---

## 🛡️ Security Features Detail

### 1. Brute Force Protection

**Mechanism:**

- Track failed login attempts per user
- Lock account for 30 minutes after 5 failed attempts
- Auto-unlock after timeout
- Reset counter on successful login

**Implementation:**

```python
# In User model
def increment_failed_login(self):
    self.failed_login_attempts += 1
    if self.failed_login_attempts >= 5:
        self.account_locked_until = datetime.utcnow() + timedelta(minutes=30)

def is_account_locked(self):
    if self.account_locked_until is None:
        return False
    if datetime.utcnow() < self.account_locked_until:
        return True
    # Auto-unlock
    self.account_locked_until = None
    self.failed_login_attempts = 0
    return False
```

### 2. API Key Management

**Features:**

- 64-character hex token (cryptographically secure)
- Optional expiration date
- Regeneration capability
- Validation on every request

**Implementation:**

```python
def generate_api_key(self, expires_in_days=None):
    self.api_key = secrets.token_hex(32)  # 64 chars
    self.api_key_created_at = datetime.utcnow()
    if expires_in_days:
        self.api_key_expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
```

### 3. Password Reset

**Flow:**

1. User requests reset (provide email)
2. Generate secure token (32 bytes, URL-safe)
3. Set expiration (1 hour)
4. Send token via email (TODO: implement email service)
5. User submits token + new password
6. Verify token validity
7. Update password
8. Clear token

**Security:**

- Token is single-use
- Expires after 1 hour
- Token cleared after use
- Password re-hashed

---

## 📦 Components

### Models

- **User Model** (`app/models/user_model.py`)
  - User data structure
  - Password hashing/verification
  - API key management
  - Security helpers

### Services

- **AuthService** (`app/services/auth_service.py`)
  - Registration logic
  - Authentication logic
  - Password reset logic
  - API key regeneration

### Controllers

- **AuthController** (`app/controllers/auth_controller.py`)
  - Request handling
  - Input validation
  - Response formatting
  - Error handling

### Decorators

- **Security Decorators** (`app/decorators/security.py`)
  - `@api_key_required` - Validate API key
  - `@internal_key_required` - Internal service auth
- **Role Decorators** (`app/decorators/roles.py`)
  - `@admin_required` - Admin only
  - `@premium_required` - Premium + Admin
  - `@role_required(role)` - Specific role

### Routes

- **Auth Routes** (`app/routes/auth_routes.py`)
  - `/register` - Create account
  - `/login` - Authenticate
  - `/logout` - End session
  - `/me` - Get user info
  - `/regenerate-api-key` - New API key
  - `/request-password-reset` - Request reset
  - `/reset-password` - Reset password

---

## 🗄️ Database Schema

Lihat [DATABASE.md](DATABASE.md) untuk detail lengkap.

**Key Fields:**

```python
# Authentication
email                    VARCHAR(120) UNIQUE NOT NULL
password_hash            VARCHAR(128) NOT NULL
api_key                 VARCHAR(64) UNIQUE NOT NULL

# Security
failed_login_attempts    INTEGER DEFAULT 0
account_locked_until     DATETIME NULL
api_key_expires_at      DATETIME NULL

# Activity
last_login              DATETIME NULL
last_activity           DATETIME NULL

# Usage & Quota
usage_count             INTEGER DEFAULT 0
monthly_quota           INTEGER DEFAULT 10
last_quota_reset        DATETIME

# Password Reset
reset_token             VARCHAR(100) NULL
reset_token_expires     DATETIME NULL
```

---

## 🔍 Untuk Developer

- **API Reference:** [API.md](API.md)
- **Developer Guide:** [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- **Security Best Practices:** [SECURITY.md](SECURITY.md)
- **Testing Guide:** [../TESTING.md](../TESTING.md)

---

## 📝 TODO / Roadmap

### Short Term

- [ ] Implement email service for password reset
- [ ] Add rate limiting per IP
- [ ] Password strength validation
- [ ] Email verification on registration

### Medium Term

- [ ] 2FA (TOTP)
- [ ] OAuth integration (Google, GitHub)
- [ ] Session management improvements
- [ ] Audit logging

### Long Term

- [ ] Passwordless login (Magic links)
- [ ] WebAuthn support
- [ ] Multi-device management
- [ ] Advanced threat detection

---

## 🤝 Contributing

Lihat [CONTRIBUTING.md](../CONTRIBUTING.md) untuk panduan lengkap.

**Quick tips:**

1. Selalu test security changes
2. Follow principle of least privilege
3. Log security events
4. Never expose sensitive data in responses
5. Validate all inputs

---

## 📚 References

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/)
