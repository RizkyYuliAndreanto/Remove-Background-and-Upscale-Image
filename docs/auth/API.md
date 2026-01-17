# 🔌 Authentication API Reference

Base URL: `http://localhost:5000/api/v1/auth`

---

## Table of Contents

- [Register](#register)
- [Login](#login)
- [Logout](#logout)
- [Get Current User](#get-current-user)
- [Regenerate API Key](#regenerate-api-key)
- [Request Password Reset](#request-password-reset)
- [Reset Password](#reset-password)

---

## Register

Create a new user account.

**Endpoint:** `POST /register`

**Authentication:** None (Public)

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Success Response (201):**

```json
{
  "status": "success",
  "message": "User registered successfully",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "role": "user",
    "api_key": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
    "usage_count": 0,
    "monthly_quota": 10,
    "quota_remaining": 10,
    "is_active": true,
    "created_at": "2026-01-17T10:00:00.000000"
  }
}
```

**Error Responses:**

| Code | Error                    | Description                      |
| ---- | ------------------------ | -------------------------------- |
| 400  | Missing fields           | Email or password not provided   |
| 400  | Email Already Registered | Email already exists in database |
| 500  | Internal server error    | Server error occurred            |

**Example:**

```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!"
  }'
```

---

## Login

Authenticate user and get API key.

**Endpoint:** `POST /login`

**Authentication:** None (Public)

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Success Response (200):**

```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "role": "user",
    "api_key": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
    "api_key_created_at": "2026-01-17T10:00:00.000000",
    "api_key_expires_at": null,
    "usage_count": 5,
    "monthly_quota": 10,
    "quota_remaining": 5,
    "last_login": "2026-01-17T10:30:00.000000",
    "is_active": true,
    "created_at": "2026-01-17T10:00:00.000000"
  }
}
```

**Error Responses:**

| Code | Error                 | Description                                                |
| ---- | --------------------- | ---------------------------------------------------------- |
| 401  | Invalid Credentials   | Wrong email or password                                    |
| 403  | Account Banned        | Account has been banned by admin                           |
| 403  | Account Locked        | Too many failed attempts. Account locked until {timestamp} |
| 500  | Internal server error | Server error occurred                                      |

**Brute Force Protection:**

- Max 5 failed attempts
- Account locked for 30 minutes after 5th failed attempt
- Counter resets on successful login

**Example:**

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

---

## Logout

End user session.

**Endpoint:** `POST /logout`

**Authentication:** `@login_required` (Flask-Login session)

**Request Body:** None

**Success Response (200):**

```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

**Example:**

```bash
curl -X POST http://localhost:5000/api/v1/auth/logout \
  -H "Cookie: session=..."
```

---

## Get Current User

Get current user information including usage stats.

**Endpoint:** `GET /me`

**Authentication:** API Key required

**Headers:**

```
X-API-KEY: your-api-key-here
```

**Success Response (200):**

```json
{
  "status": "success",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "role": "user",
    "usage_count": 5,
    "monthly_quota": 10,
    "quota_remaining": 5,
    "last_login": "2026-01-17T10:30:00.000000",
    "is_active": true,
    "created_at": "2026-01-17T10:00:00.000000",
    "updated_at": "2026-01-17T10:30:00.000000"
  }
}
```

**Error Responses:**

| Code | Error                 | Description                  |
| ---- | --------------------- | ---------------------------- |
| 401  | API Key required      | No API key in header         |
| 401  | Invalid API Key       | API key not found or invalid |
| 403  | Account Banned        | Account has been banned      |
| 500  | Internal server error | Server error occurred        |

**Example:**

```bash
curl -X GET http://localhost:5000/api/v1/auth/me \
  -H "X-API-KEY: your-api-key-here"
```

---

## Regenerate API Key

Generate new API key (old key becomes invalid).

**Endpoint:** `POST /regenerate-api-key`

**Authentication:** API Key required

**Headers:**

```
X-API-KEY: your-current-api-key
```

**Request Body (Optional):**

```json
{
  "expires_in_days": 30
}
```

**Success Response (200):**

```json
{
  "status": "success",
  "message": "API Key regenerated successfully",
  "api_key": "new-api-key-64-characters-long"
}
```

**Error Responses:**

| Code | Error                | Description               |
| ---- | -------------------- | ------------------------- |
| 401  | API Key required     | No API key in header      |
| 401  | Invalid API Key      | Current API key not found |
| 500  | Failed to regenerate | Server error occurred     |

**⚠️ Important:**

- Old API key immediately becomes invalid
- Save new API key securely
- If `expires_in_days` is set, key will expire after X days

**Example:**

```bash
curl -X POST http://localhost:5000/api/v1/auth/regenerate-api-key \
  -H "X-API-KEY: your-current-api-key" \
  -H "Content-Type: application/json" \
  -d '{"expires_in_days": 30}'
```

---

## Request Password Reset

Request a password reset token.

**Endpoint:** `POST /request-password-reset`

**Authentication:** None (Public)

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Success Response (200):**

```json
{
  "status": "success",
  "message": "If email exists, reset token has been sent",
  "reset_token": "abc123def456..." // ONLY in development mode
}
```

**Notes:**

- Always returns 200 even if email doesn't exist (security best practice)
- Token valid for 1 hour
- In production, token should be sent via email (not in response)
- Single-use token

**Error Responses:**

| Code | Error                 | Description           |
| ---- | --------------------- | --------------------- |
| 400  | Email is required     | Email not provided    |
| 500  | Internal server error | Server error occurred |

**Example:**

```bash
curl -X POST http://localhost:5000/api/v1/auth/request-password-reset \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

---

## Reset Password

Reset password using token.

**Endpoint:** `POST /reset-password`

**Authentication:** None (Public, but requires valid token)

**Request Body:**

```json
{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePassword456!"
}
```

**Success Response (200):**

```json
{
  "status": "success",
  "message": "Password reset successfully"
}
```

**Error Responses:**

| Code | Error                          | Description                                |
| ---- | ------------------------------ | ------------------------------------------ |
| 400  | Missing fields                 | Token or new_password not provided         |
| 400  | Invalid or expired reset token | Token is invalid, expired, or already used |
| 500  | Internal server error          | Server error occurred                      |

**Notes:**

- Token is single-use (cleared after successful reset)
- Token expires after 1 hour
- Password is hashed before storage

**Example:**

```bash
curl -X POST http://localhost:5000/api/v1/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123def456...",
    "new_password": "NewSecurePass456!"
  }'
```

---

## Common Error Codes

| HTTP Code | Meaning                                                     |
| --------- | ----------------------------------------------------------- |
| 200       | Success                                                     |
| 201       | Created (successful registration)                           |
| 400       | Bad Request (validation error)                              |
| 401       | Unauthorized (invalid credentials/API key)                  |
| 403       | Forbidden (account locked/banned, insufficient permissions) |
| 429       | Too Many Requests (rate limit exceeded)                     |
| 500       | Internal Server Error                                       |

---

## Rate Limiting

### Current Implementation

- No rate limiting yet (TODO)

### Planned Limits

- **Per IP:** 100 requests/hour
- **Per User (free):** 10 requests/month
- **Per User (premium):** 1000 requests/month
- **Per User (admin):** Unlimited

### Response Headers (When Implemented)

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642435200
```

---

## Security Best Practices

### For API Consumers

1. **Store API Keys Securely**

   - Never commit to version control
   - Use environment variables
   - Rotate keys regularly

2. **HTTPS Only**

   - Always use HTTPS in production
   - Never send API keys over HTTP

3. **Handle Errors Gracefully**

   - Don't expose error details to end users
   - Log errors for debugging
   - Implement retry logic with exponential backoff

4. **Validate Responses**
   - Always check `status` field
   - Handle all possible error codes
   - Verify data types

### Example Error Handling (JavaScript)

```javascript
try {
  const response = await fetch("/api/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (data.status === "success") {
    // Store API key securely
    localStorage.setItem("api_key", data.data.api_key);
  } else {
    // Handle error
    console.error(data.message);
  }
} catch (error) {
  console.error("Network error:", error);
}
```

---

## Testing

Use `test_quick.py` or `test_auth.py` for automated testing.

**Manual Testing with curl:**

```bash
# Set base URL
BASE_URL="http://localhost:5000/api/v1/auth"

# Register
curl -X POST $BASE_URL/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Login
API_KEY=$(curl -s -X POST $BASE_URL/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}' \
  | jq -r '.data.api_key')

# Get user info
curl -X GET $BASE_URL/me \
  -H "X-API-KEY: $API_KEY"
```

---

## Changelog

### v1.0.0 (Current)

- ✅ User registration & login
- ✅ API key authentication
- ✅ Password reset flow
- ✅ Brute force protection
- ✅ Usage tracking & quota
- ✅ Role-based access control

### Upcoming

- ⏳ Email verification
- ⏳ Rate limiting
- ⏳ 2FA support
- ⏳ OAuth integration
