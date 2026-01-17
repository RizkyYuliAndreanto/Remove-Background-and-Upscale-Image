# 🛡️ Security Features & Best Practices

Dokumentasi lengkap tentang fitur keamanan dalam sistem authentication.

---

## 🎯 Security Overview

Sistem authentication ini mengimplementasikan multiple layers of security untuk melindungi user data dan mencegah common attacks.

### Defense in Depth Strategy

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Network Security (HTTPS, Firewall)           │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Rate Limiting (TODO)                          │
├─────────────────────────────────────────────────────────┤
│  Layer 3: Authentication (API Keys, Sessions)           │
├─────────────────────────────────────────────────────────┤
│  Layer 4: Authorization (RBAC, Decorators)              │
├─────────────────────────────────────────────────────────┤
│  Layer 5: Input Validation                              │
├─────────────────────────────────────────────────────────┤
│  Layer 6: Data Protection (Hashing, Encryption)         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 Implemented Security Features

### 1. Password Security

#### Hashing Algorithm

- **Algorithm:** Bcrypt (via Werkzeug)
- **Work Factor:** 12 rounds (default)
- **Salt:** Automatically generated per password
- **Rainbow Table Resistant:** Yes

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Setting password
def set_password(self, password):
    self.password_hash = generate_password_hash(password)

# Verifying password
def check_password(self, password):
    return check_password_hash(self.password_hash, password)
```

#### Password Storage

```
Plain Text Password → Bcrypt Hash → Database
"MyPassword123"   →  "$2b$12$..."  →  Stored
```

**Why Bcrypt:**

- Computationally expensive (slows brute force)
- Adaptive (can increase work factor over time)
- Built-in salt
- Industry standard

### 2. Brute Force Protection

#### Mechanism

- **Max Attempts:** 5 failed logins
- **Lock Duration:** 30 minutes
- **Counter Reset:** On successful login
- **Auto Unlock:** After timeout expires

#### Implementation Flow

```python
def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()

    # Check if locked
    if user and user.is_account_locked():
        raise ValueError(f"Account locked until {user.account_locked_until}")

    # Verify password
    if user and user.check_password(password):
        user.reset_failed_login()  # Reset counter
        user.last_login = datetime.utcnow()
        db.session.commit()
        return user
    else:
        # Increment failed attempts
        if user:
            user.increment_failed_login()
            db.session.commit()
        return None
```

#### Database Fields

```python
failed_login_attempts = db.Column(db.Integer, default=0)
account_locked_until = db.Column(db.DateTime, nullable=True)
```

### 3. API Key Management

#### Key Generation

```python
import secrets

def generate_api_key(self, expires_in_days=None):
    # Generate 64-character hex string (256 bits of entropy)
    self.api_key = secrets.token_hex(32)
    self.api_key_created_at = datetime.utcnow()

    if expires_in_days:
        self.api_key_expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
```

**Security Properties:**

- **Length:** 64 characters
- **Entropy:** 256 bits (cryptographically secure)
- **Uniqueness:** Database constraint ensures uniqueness
- **Expiration:** Optional automatic expiration

#### Key Validation

```python
@api_key_required
def protected_endpoint():
    # g.current_user is automatically set by decorator
    return jsonify({"user": g.current_user.email})

# Decorator implementation
def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')

        if not api_key:
            return jsonify({"error": "API Key Missing"}), 401

        user = User.query.filter_by(api_key=api_key).first()

        if not user or not user.is_api_key_valid():
            return jsonify({"error": "Invalid API Key"}), 401

        if not user.is_active_status:
            return jsonify({"error": "Account Banned"}), 403

        g.current_user = user
        user.update_activity()
        db.session.commit()

        return f(*args, **kwargs)
    return decorated
```

### 4. Password Reset Security

#### Token Generation

```python
def generate_reset_token(self):
    # URL-safe 32-byte token (43 characters base64)
    self.reset_token = secrets.token_urlsafe(32)
    self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    return self.reset_token
```

#### Security Features

- **Single Use:** Token cleared after successful reset
- **Time Limited:** 1 hour expiration
- **Unique:** Each reset generates new token
- **Secure Random:** Uses `secrets` module

#### Reset Flow

```
1. User requests reset (provides email)
2. Server generates token + expiration
3. Token sent via email (TODO: implement email)
4. User submits token + new password
5. Server validates token (exists, not expired)
6. Password updated + token cleared
```

### 5. Session Management

#### Flask-Login Integration

```python
from flask_login import LoginManager, login_user, logout_user

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
```

#### Session Security

- **Secure Cookies:** HTTP-only, Secure flag in production
- **Session Timeout:** Configurable
- **CSRF Protection:** Enabled by default

### 6. Role-Based Access Control (RBAC)

#### Roles

```python
# User roles
ROLES = ['user', 'premium', 'admin']

# Default role on registration
role = db.Column(db.String(20), default='user', nullable=False)
```

#### Authorization Decorators

```python
@admin_required
def admin_panel():
    # Only admins can access
    pass

@premium_required
def premium_feature():
    # Premium and admin can access
    pass

@role_required('editor')
def edit_content():
    # Only editors can access
    pass
```

#### Implementation

```python
def admin_required(f):
    @wraps(f)
    @api_key_required  # Also validates API key
    def decorated(*args, **kwargs):
        if g.current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated
```

### 7. Usage Tracking & Quota

#### Quota Enforcement

```python
def has_quota_remaining(self):
    """Check if user has remaining quota"""
    if self.role in ['admin', 'premium']:
        return True  # Unlimited

    self.check_and_reset_quota()  # Auto-reset if 30 days passed
    return self.usage_count < self.monthly_quota
```

#### Protection Against Abuse

- **Free Users:** 10 requests/month
- **Premium Users:** 1000 requests/month
- **Admin:** Unlimited
- **Auto Reset:** Every 30 days

---

## 🚨 Threat Model & Mitigations

### 1. Brute Force Attacks

**Threat:** Attacker tries many password combinations

**Mitigations:**

- ✅ Account locking after 5 failed attempts
- ✅ 30-minute lockout period
- ⏳ Rate limiting (TODO)
- ⏳ CAPTCHA after 3 failed attempts (TODO)

### 2. Credential Stuffing

**Threat:** Using leaked credentials from other breaches

**Mitigations:**

- ✅ Unique password hashing per user (salt)
- ⏳ Check against common passwords database (TODO)
- ⏳ Monitor for suspicious login patterns (TODO)

### 3. SQL Injection

**Threat:** Malicious SQL in user inputs

**Mitigations:**

- ✅ SQLAlchemy ORM (parameterized queries)
- ✅ Input validation
- ✅ No raw SQL queries

```python
# ✅ Safe: Parameterized query
user = User.query.filter_by(email=email).first()

# ❌ Unsafe: String concatenation
# user = db.execute(f"SELECT * FROM user WHERE email = '{email}'")
```

### 4. XSS (Cross-Site Scripting)

**Threat:** Injecting malicious JavaScript

**Mitigations:**

- ✅ JSON responses (no HTML rendering)
- ✅ Content-Type headers
- ⏳ CSP headers (TODO)

### 5. CSRF (Cross-Site Request Forgery)

**Threat:** Unauthorized commands from authenticated user

**Mitigations:**

- ✅ API key required for state-changing operations
- ✅ Flask-WTF CSRF protection (for forms)
- ⏳ SameSite cookies (TODO)

### 6. Session Hijacking

**Threat:** Stealing session tokens

**Mitigations:**

- ✅ Secure, HTTP-only cookies
- ✅ Short session lifetime
- ⏳ IP address validation (TODO)
- ⏳ User-Agent validation (TODO)

### 7. API Key Theft

**Threat:** Stolen API keys used maliciously

**Mitigations:**

- ✅ Key expiration (optional)
- ✅ Key regeneration capability
- ✅ Usage tracking per key
- ⏳ IP whitelisting (TODO)
- ⏳ Anomaly detection (TODO)

### 8. Denial of Service (DoS)

**Threat:** Overwhelming server with requests

**Mitigations:**

- ⏳ Rate limiting per IP (TODO)
- ⏳ Rate limiting per user (TODO)
- ⏳ Request size limits (TODO)
- ⏳ Timeout configurations (TODO)

---

## 🔍 Security Audit Checklist

### Pre-Production

- [ ] **Authentication**

  - [ ] Passwords properly hashed (bcrypt)
  - [ ] No plain text passwords in logs
  - [ ] Brute force protection enabled
  - [ ] Session timeout configured
  - [ ] API keys cryptographically secure

- [ ] **Authorization**

  - [ ] RBAC properly implemented
  - [ ] Default deny principle
  - [ ] Least privilege principle
  - [ ] No privilege escalation paths

- [ ] **Input Validation**

  - [ ] All inputs validated
  - [ ] Email format validation
  - [ ] Password strength requirements
  - [ ] SQL injection protected (ORM)
  - [ ] No command injection risks

- [ ] **Data Protection**

  - [ ] Sensitive data encrypted at rest
  - [ ] HTTPS enforced (production)
  - [ ] Secure cookie flags set
  - [ ] No sensitive data in URLs
  - [ ] No sensitive data in logs

- [ ] **Error Handling**

  - [ ] Generic error messages (no info leak)
  - [ ] Proper exception handling
  - [ ] No stack traces in production
  - [ ] Failed logins logged
  - [ ] Security events monitored

- [ ] **Dependencies**
  - [ ] All packages up to date
  - [ ] No known vulnerabilities
  - [ ] Minimal dependencies
  - [ ] Regular security updates

### Ongoing Monitoring

- [ ] Failed login attempts tracked
- [ ] API key usage monitored
- [ ] Quota violations logged
- [ ] Suspicious patterns detected
- [ ] Regular security audits
- [ ] Penetration testing

---

## 📊 Security Logging

### What to Log

```python
# Successful events
logger.info(f"User logged in: {user.email}")
logger.info(f"API key regenerated: {user.email}")

# Security events
logger.warning(f"Failed login attempt: {email}")
logger.warning(f"Account locked: {user.email}")
logger.warning(f"Invalid API key used: {api_key[:10]}...")

# Critical events
logger.error(f"Multiple failed logins from IP: {ip}")
logger.critical(f"Potential breach detected: {details}")
```

### What NOT to Log

```python
# ❌ Never log sensitive data
logger.info(f"Password: {password}")  # NO!
logger.info(f"API Key: {api_key}")    # NO!
logger.info(f"Token: {reset_token}")  # NO!

# ✅ Log safely
logger.info(f"Password reset for: {email}")
logger.info(f"API key used: {api_key[:10]}...")
```

---

## 🔧 Security Configuration

### Production Settings

```python
# config/config.py
class ProductionConfig:
    DEBUG = False
    TESTING = False

    # Session Security
    SESSION_COOKIE_SECURE = True      # HTTPS only
    SESSION_COOKIE_HTTPONLY = True    # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'   # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    # Security Headers
    SEND_FILE_MAX_AGE_DEFAULT = 0

    # Database
    SQLALCHEMY_ECHO = False           # Don't log SQL queries
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### Security Headers (TODO)

```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

---

## 🚀 Security Roadmap

### Phase 1 (Current)

- ✅ Password hashing
- ✅ API key authentication
- ✅ Brute force protection
- ✅ Password reset
- ✅ RBAC

### Phase 2 (Next)

- ⏳ Rate limiting
- ⏳ Email verification
- ⏳ Security headers
- ⏳ Audit logging

### Phase 3 (Future)

- ⏳ 2FA (TOTP)
- ⏳ OAuth integration
- ⏳ IP whitelisting
- ⏳ Anomaly detection

### Phase 4 (Advanced)

- ⏳ WebAuthn support
- ⏳ Device fingerprinting
- ⏳ Advanced threat detection
- ⏳ Security operations center (SOC)

---

## 📚 Security Resources

### Standards & Guidelines

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/)
- [CWE Top 25](https://cwe.mitre.org/top25/)

### Tools

- [Safety](https://pypi.org/project/safety/) - Check dependencies for vulnerabilities
- [Bandit](https://github.com/PyCQA/bandit) - Security linter for Python
- [OWASP ZAP](https://www.zaproxy.org/) - Web app security scanner

### Run Security Checks

```bash
# Check for vulnerable dependencies
pip install safety
safety check

# Static security analysis
pip install bandit
bandit -r app/

# Check for secrets in code
pip install detect-secrets
detect-secrets scan
```

---

## 🆘 Security Incident Response

### If Breach Detected

1. **Immediate Actions**

   - Revoke all API keys
   - Force password resets
   - Lock affected accounts
   - Block malicious IPs

2. **Investigation**

   - Review logs
   - Identify scope
   - Determine root cause
   - Document timeline

3. **Remediation**

   - Patch vulnerabilities
   - Update dependencies
   - Improve monitoring
   - Deploy fixes

4. **Communication**
   - Notify affected users
   - Disclose responsibly
   - Update security policies
   - Lessons learned document

### Emergency Contacts

```python
# config/security.py
SECURITY_TEAM = {
    'email': 'security@example.com',
    'phone': '+1-xxx-xxx-xxxx',
    'on_call': 'https://pagerduty.com/xxx'
}
```

---

## ✅ Security Best Practices Summary

1. **Always use HTTPS in production**
2. **Hash passwords with bcrypt (never plain text)**
3. **Validate all inputs**
4. **Use parameterized queries (ORM)**
5. **Implement rate limiting**
6. **Log security events (but not sensitive data)**
7. **Keep dependencies updated**
8. **Follow principle of least privilege**
9. **Default deny for authorization**
10. **Regular security audits**

---

**Security is not a feature, it's a foundation. 🛡️**
