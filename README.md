# 🖼️ Background Remover & Upscale Image API

API backend untuk remove background dan upscale image menggunakan AI, dengan sistem authentication dan authorization yang robust.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

### 🔐 Authentication & Security

- ✅ Email + Password authentication
- ✅ API Key based access
- ✅ Brute force protection (account lock after 5 failed attempts)
- ✅ Password reset with secure tokens
- ✅ Role-based access control (RBAC)
- ✅ API key expiration & regeneration
- ✅ Usage tracking & monthly quota

### 🎨 Image Processing (Coming Soon)

- ⏳ AI-powered background removal (rembg + U2-Net)
- ⏳ Image upscaling (OpenCV)
- ⏳ Multiple file format support
- ⏳ Batch processing
- ⏳ Cloud storage integration

### 👥 User Management

- ✅ User registration & login
- ✅ Admin panel
- ✅ User ban/unban
- ✅ Usage statistics
- ✅ Activity tracking

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (production) or SQLite (development)
- Git

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd Backend

# 2. Create virtual environment
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# 5. Initialize database
flask db upgrade

# 6. Create admin user
python create_admin.py

# 7. Run the application
python main.py
```

Server will start at `http://127.0.0.1:5000`

---

## 📚 Documentation

### Quick Links

- **[API Documentation](docs/auth/API.md)** - Complete API reference
- **[Developer Guide](docs/auth/DEVELOPER_GUIDE.md)** - Development guide
- **[Security Features](docs/auth/SECURITY.md)** - Security documentation
- **[Project Structure](docs/architecture/PROJECT_STRUCTURE.md)** - Code organization
- **[Database Schema](docs/auth/DATABASE.md)** - Database details

### For Contributors

- [Contributing Guide](docs/CONTRIBUTING.md) - How to contribute
- [Code Style Guide](docs/CODE_STYLE.md) - Coding standards
- [Testing Guide](docs/TESTING.md) - Testing guidelines

---

## 🔑 API Quick Reference

### Base URL

```
http://localhost:5000/api/v1
```

### Authentication Endpoints

| Method | Endpoint                       | Description            |
| ------ | ------------------------------ | ---------------------- |
| POST   | `/auth/register`               | Create new account     |
| POST   | `/auth/login`                  | Login & get API key    |
| POST   | `/auth/logout`                 | Logout                 |
| GET    | `/auth/me`                     | Get current user info  |
| POST   | `/auth/regenerate-api-key`     | Generate new API key   |
| POST   | `/auth/request-password-reset` | Request password reset |
| POST   | `/auth/reset-password`         | Reset password         |

### Example: Register

```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

### Example: Login

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

### Example: Protected Endpoint

```bash
curl -X GET http://localhost:5000/api/v1/auth/me \
  -H "X-API-KEY: your-api-key-here"
```

---

## 🛡️ Security Features

### Implemented

- ✅ **Password Hashing** - Bcrypt with salt
- ✅ **Brute Force Protection** - 5 attempts, 30 min lock
- ✅ **API Key Authentication** - 64-char secure tokens
- ✅ **Token Expiration** - Optional API key expiration
- ✅ **Password Reset** - Secure, time-limited tokens
- ✅ **Usage Quota** - Prevent abuse
- ✅ **Account Status** - Ban/unban capability

### Planned

- ⏳ Rate limiting per IP
- ⏳ Email verification
- ⏳ 2FA (Two-Factor Authentication)
- ⏳ OAuth integration
- ⏳ Advanced threat detection

---

## 🎯 User Roles & Quotas

| Role            | Monthly Quota | Features                   |
| --------------- | ------------- | -------------------------- |
| **user** (free) | 10 requests   | Basic features             |
| **premium**     | 1000 requests | All features               |
| **admin**       | Unlimited     | Admin panel + all features |

---

## 🗄️ Database Schema

### User Table

| Column        | Type     | Description                              |
| ------------- | -------- | ---------------------------------------- |
| id            | UUID     | Primary key                              |
| email         | String   | User email (unique)                      |
| password_hash | String   | Bcrypt hashed password                   |
| role          | String   | user/premium/admin                       |
| api_key       | String   | 64-char authentication key               |
| usage_count   | Integer  | API calls this month                     |
| monthly_quota | Integer  | Monthly limit                            |
| last_login    | DateTime | Last login timestamp                     |
| ...           | ...      | [See full schema](docs/auth/DATABASE.md) |

---

## 🧪 Testing

### Quick Test

```bash
# Activate venv first
.\venv\Scripts\Activate.ps1

# Run quick test
python test_quick.py
```

### Comprehensive Test

```bash
python test_auth.py
```

### Unit Tests (TODO)

```bash
pytest tests/
```

---

## 📁 Project Structure

```
Backend/
├── app/                    # Main application
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   ├── controllers/       # Request handlers
│   ├── routes/            # URL routing
│   └── decorators/        # Auth decorators
├── config/                # Configuration
├── migrations/            # Database migrations
├── docs/                  # Documentation
├── tests/                 # Test files
├── main.py               # Entry point
├── requirements.txt      # Dependencies
└── README.md            # This file
```

[See detailed structure →](docs/architecture/PROJECT_STRUCTURE.md)

---

## 🛠️ Tech Stack

### Backend Framework

- **Flask** - Micro web framework
- **Flask-SQLAlchemy** - ORM
- **Flask-Migrate** - Database migrations
- **Flask-Login** - Session management
- **Flask-CORS** - CORS support

### Security

- **Werkzeug** - Password hashing (bcrypt)
- **PyJWT** - JSON Web Tokens
- **secrets** - Secure token generation

### Image Processing

- **Pillow** - Image manipulation
- **rembg** - AI background removal
- **opencv-python** - Image upscaling
- **numpy** - Array operations

### Database

- **PostgreSQL** - Production database
- **SQLite** - Development database

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Flask
SECRET_KEY=your-secret-key-here
DEBUG=True
HOST=127.0.0.1
PORT=5000

# Database
DATABASE_URL=sqlite:///instance/app.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Security
INTERNAL_SERVICE_KEY=internal-service-key

# Email (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

## 📈 Roadmap

### Phase 1: Authentication ✅ (Current)

- ✅ User registration & login
- ✅ API key authentication
- ✅ Password reset
- ✅ Brute force protection
- ✅ Usage tracking

### Phase 2: Core Features (In Progress)

- ⏳ Background removal endpoint
- ⏳ Image upscaling endpoint
- ⏳ File upload handling
- ⏳ Cloud storage integration

### Phase 3: Enhancement

- ⏳ Rate limiting
- ⏳ Email verification
- ⏳ Admin dashboard
- ⏳ Usage analytics

### Phase 4: Advanced

- ⏳ 2FA support
- ⏳ OAuth integration
- ⏳ Batch processing
- ⏳ Webhook notifications

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md).

### Development Workflow

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests
5. Update documentation
6. Commit (`git commit -m 'feat: Add amazing feature'`)
7. Push (`git push origin feature/amazing-feature`)
8. Create Pull Request

---

## 🐛 Issue Reporting

Found a bug or security issue?

- **Bugs:** Open an issue on GitHub
- **Security:** Email security@example.com (do not open public issue)
- **Questions:** Use GitHub Discussions

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Authors

- **Your Name** - _Initial work_ - [GitHub Profile](https://github.com/username)

---

## 🙏 Acknowledgments

- [rembg](https://github.com/danielgatis/rembg) - AI background removal
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [U2-Net](https://github.com/xuebinqin/U-2-Net) - Salient object detection

---

## 📞 Support

- **Documentation:** [docs/README.md](docs/README.md)
- **API Reference:** [docs/auth/API.md](docs/auth/API.md)
- **Email:** support@example.com
- **Discord:** [Join our server](#)

---

## 🌟 Star History

If this project helps you, please give it a ⭐️!

---

**Built with ❤️ by the Background Remover Team**
