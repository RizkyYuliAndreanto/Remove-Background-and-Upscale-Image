# 🔐 API Authentication Documentation

## 📋 Base URL

```
http://localhost:5000/api/auth
```

---

## 🆕 Fitur Auth yang Ditambahkan

### ✅ Fitur Keamanan Baru:

1. **Brute Force Protection** - Account lock setelah 5 kali login gagal
2. **API Key Expiration** - API key bisa expired (default: tidak expired)
3. **Password Reset** - Reset password menggunakan token
4. **API Key Regeneration** - User bisa regenerate API key
5. **Usage Tracking** - Track jumlah pemakaian API per user
6. **Monthly Quota** - Batasan pemakaian bulanan (free: 10, premium: 1000)
7. **Account Lock Management** - Temporary account lock untuk keamanan
8. **Activity Tracking** - Last login & last activity tracking

---

## 📚 API Endpoints

### 1. Register User

**POST** `/api/auth/register`

```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response (201):
{
  "status": "success",
  "message": "User registered successfully",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "role": "user",
    "created_at": "2026-01-17T10:00:00",
    "updated_at": "2026-01-17T10:00:00"
  }
}
```

---

### 2. Login

**POST** `/api/auth/login`

```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response (200):
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "id": "uuid-here",
    "email": "user@example.com",
    "role": "user",
    "api_key": "your-api-key-here",
    "created_at": "2026-01-17T10:00:00"
  }
}

Error - Account Locked (403):
{
  "status": "error",
  "message": "Account locked. Try again after 2026-01-17 11:00:00"
}

Error - Account Banned (403):
{
  "status": "error",
  "message": "Account is banned, contact support"
}
```

**⚠️ Brute Force Protection:**

- Setelah 5 kali login gagal → Account locked 30 menit
- Failed attempts di-reset setelah login berhasil

---

### 3. Get Current User Info 🆕

**GET** `/api/auth/me`

**Headers:**

```
X-API-KEY: your-api-key-here
```

```json
Response (200):
{
  "status": "success",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "role": "user",
    "usage_count": 5,
    "monthly_quota": 10,
    "remaining_quota": 5,
    "last_login": "2026-01-17T10:00:00",
    "last_activity": "2026-01-17T10:30:00",
    "api_key_created_at": "2026-01-17T10:00:00",
    "api_key_expires_at": null,
    "created_at": "2026-01-17T10:00:00"
  }
}
```

---

### 4. Regenerate API Key 🆕

**POST** `/api/auth/regenerate-api-key`

**Headers:**

```
X-API-KEY: your-current-api-key
```

```json
Request (Optional):
{
  "expires_in_days": 30
}

Response (200):
{
  "status": "success",
  "message": "API Key regenerated successfully",
  "api_key": "new-api-key-here"
}
```

**⚠️ Important:**

- Old API key akan langsung invalid
- Simpan API key baru dengan aman
- Jika set `expires_in_days`, API key akan expired setelah X hari

---

### 5. Request Password Reset 🆕

**POST** `/api/auth/request-password-reset`

```json
Request:
{
  "email": "user@example.com"
}

Response (200):
{
  "status": "success",
  "message": "If email exists, reset token has been sent",
  "reset_token": "abc123def456"  // HANYA untuk development!
}
```

**⚠️ Production Note:**

- Token seharusnya dikirim via email
- Token valid selama 1 jam
- Response akan selalu success (security best practice)

---

### 6. Reset Password 🆕

**POST** `/api/auth/reset-password`

```json
Request:
{
  "token": "abc123def456",
  "new_password": "NewSecurePass456!"
}

Response (200):
{
  "status": "success",
  "message": "Password reset successfully"
}

Error - Invalid/Expired Token (400):
{
  "status": "error",
  "message": "Invalid or expired reset token"
}
```

---

## 🔒 Security Features

### 1. Brute Force Protection

- Max 5 failed login attempts
- Account locked for 30 minutes
- Counter reset after successful login

### 2. API Key Security

- 64 character hex token (cryptographically secure)
- Optional expiration date
- Can be regenerated anytime
- Checked on every protected endpoint

### 3. Password Security

- Hashed using Werkzeug (bcrypt)
- Never stored in plaintext
- Minimum requirements enforced (dapat ditambahkan validator)

### 4. Usage Tracking

- Every API call tracked
- Monthly quota enforced
- Auto-reset setiap bulan
- Different limits for free/premium users

---

## 📊 User Roles & Quotas

| Role            | Monthly Quota | Features                   |
| --------------- | ------------- | -------------------------- |
| **user** (free) | 10 requests   | Basic features             |
| **premium**     | 1000 requests | All features               |
| **admin**       | Unlimited     | Admin panel + all features |

---

## 🛡️ Protected Endpoints

Semua endpoint yang memerlukan authentication harus include header:

```
X-API-KEY: your-api-key-here
```

Contoh endpoint protected:

- `/api/remove-background` → Premium users only
- `/api/upscale-image` → Premium users only
- `/api/admin/*` → Admin only

---

## ⚠️ Error Codes

| Code | Meaning               | Action                                            |
| ---- | --------------------- | ------------------------------------------------- |
| 401  | Unauthorized          | Provide valid API key                             |
| 403  | Forbidden             | Account locked/banned or insufficient permissions |
| 429  | Too Many Requests     | Quota exceeded, upgrade or wait                   |
| 500  | Internal Server Error | Contact support                                   |

---

## 🧪 Testing

Jalankan test suite:

```bash
python test_auth.py
```

Atau test manual dengan curl:

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'

# Get User Info
curl -X GET http://localhost:5000/api/auth/me \
  -H "X-API-KEY: your-api-key-here"
```

---

## 📝 TODO (Untuk Production)

- [ ] Implement email service untuk password reset
- [ ] Add rate limiting (Flask-Limiter)
- [ ] Add password strength validator
- [ ] Add email verification
- [ ] Add 2FA (Two-Factor Authentication)
- [ ] Add IP-based throttling
- [ ] Add audit logging
- [ ] Setup monitoring & alerts
- [ ] Add CAPTCHA untuk repeated failed logins
