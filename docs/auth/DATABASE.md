# 🗄️ Database Schema - Authentication

## User Table

Table name: `user`

### Schema

| Column                    | Type         | Constraints              | Description                           |
| ------------------------- | ------------ | ------------------------ | ------------------------------------- |
| **id**                    | VARCHAR(36)  | PRIMARY KEY              | UUID as string                        |
| **email**                 | VARCHAR(120) | UNIQUE, NOT NULL         | User email address                    |
| **password_hash**         | VARCHAR(128) | NOT NULL                 | Bcrypt hashed password                |
| **role**                  | VARCHAR(20)  | NOT NULL, DEFAULT 'user' | User role (user/premium/admin)        |
| **api_key**               | VARCHAR(64)  | UNIQUE, NOT NULL         | 64-char hex API key                   |
| **is_active_status**      | BOOLEAN      | DEFAULT TRUE             | Account active/banned status          |
| **failed_login_attempts** | INTEGER      | DEFAULT 0                | Count of failed login attempts        |
| **account_locked_until**  | DATETIME     | NULLABLE                 | Unlock timestamp (NULL if not locked) |
| **last_login**            | DATETIME     | NULLABLE                 | Last successful login                 |
| **last_activity**         | DATETIME     | NULLABLE                 | Last API activity                     |
| **api_key_created_at**    | DATETIME     | NOT NULL                 | API key generation timestamp          |
| **api_key_expires_at**    | DATETIME     | NULLABLE                 | API key expiration (NULL = no expiry) |
| **usage_count**           | INTEGER      | DEFAULT 0                | Total API calls this month            |
| **monthly_quota**         | INTEGER      | DEFAULT 10               | Monthly API call limit                |
| **last_quota_reset**      | DATETIME     | NOT NULL                 | Last quota reset timestamp            |
| **reset_token**           | VARCHAR(100) | NULLABLE                 | Password reset token                  |
| **reset_token_expires**   | DATETIME     | NULLABLE                 | Reset token expiration                |
| **created_at**            | DATETIME     | NOT NULL                 | Account creation timestamp            |
| **updated_at**            | DATETIME     | NOT NULL                 | Last update timestamp                 |

### Indexes

```sql
CREATE UNIQUE INDEX idx_user_email ON user(email);
CREATE UNIQUE INDEX idx_user_api_key ON user(api_key);
CREATE INDEX idx_user_role ON user(role);
CREATE INDEX idx_user_is_active ON user(is_active_status);
CREATE INDEX idx_user_reset_token ON user(reset_token);
```

### SQL Schema (PostgreSQL)

```sql
CREATE TABLE "user" (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    api_key VARCHAR(64) UNIQUE NOT NULL,
    is_active_status BOOLEAN DEFAULT TRUE,

    -- Security Features
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked_until TIMESTAMP NULL,

    -- Activity Tracking
    last_login TIMESTAMP NULL,
    last_activity TIMESTAMP NULL,

    -- API Key Management
    api_key_created_at TIMESTAMP NOT NULL,
    api_key_expires_at TIMESTAMP NULL,

    -- Usage & Quota
    usage_count INTEGER DEFAULT 0,
    monthly_quota INTEGER DEFAULT 10,
    last_quota_reset TIMESTAMP NOT NULL,

    -- Password Reset
    reset_token VARCHAR(100) NULL,
    reset_token_expires TIMESTAMP NULL,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE UNIQUE INDEX idx_user_email ON "user"(email);
CREATE UNIQUE INDEX idx_user_api_key ON "user"(api_key);
CREATE INDEX idx_user_role ON "user"(role);
CREATE INDEX idx_user_is_active ON "user"(is_active_status);
CREATE INDEX idx_user_reset_token ON "user"(reset_token);
```

### SQLAlchemy Model

```python
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    # Primary Key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Authentication
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    is_active_status = db.Column(db.Boolean, default=True)

    # Security Features
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime, nullable=True)

    # Activity Tracking
    last_login = db.Column(db.DateTime, nullable=True)
    last_activity = db.Column(db.DateTime, nullable=True)

    # API Key Management
    api_key_created_at = db.Column(db.DateTime, default=datetime.utcnow)
    api_key_expires_at = db.Column(db.DateTime, nullable=True)

    # Usage & Quota
    usage_count = db.Column(db.Integer, default=0)
    monthly_quota = db.Column(db.Integer, default=10)
    last_quota_reset = db.Column(db.DateTime, default=datetime.utcnow)

    # Password Reset
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## Field Details

### id (Primary Key)

- **Type:** UUID stored as string
- **Generated:** Automatically on creation
- **Example:** `"550e8400-e29b-41d4-a716-446655440000"`
- **Why UUID:**
  - Globally unique
  - Non-sequential (security)
  - Easy to merge databases

### email

- **Type:** String (max 120 chars)
- **Validation:** Email format via email-validator
- **Unique:** Yes
- **Case-sensitive:** No (normalized to lowercase)

### password_hash

- **Type:** String (128 chars)
- **Algorithm:** Bcrypt (via Werkzeug)
- **Never exposed:** Never returned in API responses
- **Example:** `"$2b$12$KixLQ7..."`

### role

- **Values:** `'user'`, `'premium'`, `'admin'`
- **Default:** `'user'`
- **Used for:** RBAC (Role-Based Access Control)
- **Quota mapping:**
  - `user`: 10 requests/month
  - `premium`: 1000 requests/month
  - `admin`: unlimited

### api_key

- **Type:** 64-character hex string
- **Generated:** `secrets.token_hex(32)`
- **Unique:** Yes
- **Example:** `"a1b2c3d4e5f6..."`
- **Security:** Cryptographically secure random

### is_active_status

- **Type:** Boolean
- **Default:** `TRUE`
- **Usage:** Ban/unban users
- **Effect:** Blocks all API access when `FALSE`

### failed_login_attempts

- **Type:** Integer
- **Default:** 0
- **Increments:** On failed login
- **Resets:** On successful login
- **Threshold:** 5 attempts = account lock

### account_locked_until

- **Type:** Timestamp
- **Default:** `NULL` (not locked)
- **Set when:** 5th failed login attempt
- **Duration:** 30 minutes from lock time
- **Auto-unlock:** Checked on next login attempt

### last_login

- **Type:** Timestamp
- **Updated:** On successful login
- **Nullable:** Yes (NULL for never logged in)

### last_activity

- **Type:** Timestamp
- **Updated:** On every API request (via decorator)
- **Use case:** Detect inactive accounts

### api_key_created_at

- **Type:** Timestamp
- **Set:** When API key generated/regenerated
- **Use case:** Track key age

### api_key_expires_at

- **Type:** Timestamp
- **Default:** `NULL` (never expires)
- **Optional:** Set via `expires_in_days` parameter
- **Validation:** Checked on every API request

### usage_count

- **Type:** Integer
- **Default:** 0
- **Increments:** On every processed API request
- **Resets:** Every 30 days (see `last_quota_reset`)

### monthly_quota

- **Type:** Integer
- **Default:** 10 (free tier)
- **Enforcement:** Before processing request
- **Admin/Premium:** Can be set higher or unlimited

### last_quota_reset

- **Type:** Timestamp
- **Default:** Account creation time
- **Resets:** Every 30 days
- **Logic:** If `now - last_quota_reset >= 30 days`, reset usage_count

### reset_token

- **Type:** String (100 chars)
- **Generated:** `secrets.token_urlsafe(32)`
- **Single-use:** Cleared after successful reset
- **Example:** `"abc123DEF456xyz..."`

### reset_token_expires

- **Type:** Timestamp
- **Lifetime:** 1 hour from generation
- **Validation:** Must be before current time

### created_at / updated_at

- **Type:** Timestamp
- **Auto-managed:** By SQLAlchemy
- **UTC:** Always stored in UTC

---

## Migrations

### Initial Migration

```bash
# Create initial schema
flask db migrate -m "Initial user table"
flask db upgrade
```

### Add Security Features

```bash
# Add brute force protection & other features
flask db migrate -m "Add security features and usage tracking"
flask db upgrade
```

### View Migrations

```bash
# List all migrations
flask db history

# Current version
flask db current

# Rollback last migration
flask db downgrade -1
```

---

## Data Relationships

### Future Tables (Planned)

```
user (1) ─────< (Many) processed_images
  │
  └─────< (Many) usage_logs
  │
  └─────< (Many) sessions
```

**processed_images:**

- Store info about processed images
- Foreign key: `user_id`
- Fields: `original_filename`, `processed_path`, `process_type`, etc.

**usage_logs:**

- Detailed API usage history
- Foreign key: `user_id`
- Fields: `endpoint`, `timestamp`, `ip_address`, `response_code`

**sessions:**

- Active login sessions
- Foreign key: `user_id`
- Fields: `session_token`, `ip_address`, `user_agent`, `expires_at`

---

## Query Examples

### Common Queries

```python
# Find user by email
user = User.query.filter_by(email='user@example.com').first()

# Find user by API key
user = User.query.filter_by(api_key='abc123...').first()

# Find all premium users
premium_users = User.query.filter_by(role='premium').all()

# Find locked accounts
locked = User.query.filter(User.account_locked_until > datetime.utcnow()).all()

# Find users over quota
over_quota = User.query.filter(
    User.usage_count >= User.monthly_quota,
    User.role == 'user'
).all()

# Find inactive users (no login in 90 days)
from datetime import timedelta
threshold = datetime.utcnow() - timedelta(days=90)
inactive = User.query.filter(User.last_login < threshold).all()
```

### Bulk Operations

```python
# Reset all quotas (monthly job)
from datetime import timedelta
users = User.query.filter(
    User.last_quota_reset < datetime.utcnow() - timedelta(days=30)
).all()
for user in users:
    user.usage_count = 0
    user.last_quota_reset = datetime.utcnow()
db.session.commit()

# Unlock expired locks
User.query.filter(
    User.account_locked_until < datetime.utcnow()
).update({
    'account_locked_until': None,
    'failed_login_attempts': 0
})
db.session.commit()
```

---

## Performance Considerations

### Indexes

- ✅ `email` - UNIQUE index (for login lookup)
- ✅ `api_key` - UNIQUE index (for API auth)
- ✅ `role` - Regular index (for role filtering)
- ✅ `is_active_status` - Regular index (for active user queries)
- ✅ `reset_token` - Regular index (for password reset)

### Query Optimization

```python
# ❌ Bad: Load all fields when only need few
users = User.query.all()

# ✅ Good: Select only needed fields
from sqlalchemy import select
stmt = select(User.id, User.email, User.role)
results = db.session.execute(stmt).all()

# ✅ Good: Use pagination
users = User.query.paginate(page=1, per_page=20)
```

### Caching Strategy (Future)

```python
# Cache active users' API keys (Redis)
# TTL: 5 minutes
@cache.memoize(timeout=300)
def get_user_by_api_key(api_key):
    return User.query.filter_by(api_key=api_key).first()
```

---

## Backup & Recovery

### Backup User Data

```bash
# PostgreSQL
pg_dump -U username -t user database_name > user_backup.sql

# SQLite
sqlite3 database.db ".dump user" > user_backup.sql
```

### Restore

```bash
# PostgreSQL
psql -U username database_name < user_backup.sql

# SQLite
sqlite3 database.db < user_backup.sql
```

---

## Security Notes

### Sensitive Fields

Never expose in API responses:

- ❌ `password_hash`
- ❌ `reset_token`
- ⚠️ `api_key` (only on login/register)

### Encryption at Rest

For production, consider encrypting:

- API keys (reversible encryption)
- Reset tokens
- Email addresses (PII)

### Audit Logging

Log all changes to:

- Role changes
- Account status changes
- Password resets
- API key regenerations
