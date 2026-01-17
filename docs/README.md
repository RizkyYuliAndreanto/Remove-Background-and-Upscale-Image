# 📚 Documentation

Selamat datang di dokumentasi **Background Remover & Upscale Image API**!

Dokumentasi ini dibuat untuk memudahkan contributor dalam memahami, mengembangkan, dan memelihara sistem.

---

## 📂 Struktur Dokumentasi

### 🔐 Authentication System

- [Overview](auth/README.md) - Gambaran umum sistem auth
- [API Reference](auth/API.md) - Dokumentasi endpoint lengkap
- [Security Features](auth/SECURITY.md) - Fitur keamanan
- [Developer Guide](auth/DEVELOPER_GUIDE.md) - Panduan development
- [Database Schema](auth/DATABASE.md) - Struktur database auth

### 🏗️ Architecture

- [Project Structure](architecture/PROJECT_STRUCTURE.md) - Struktur folder project
- [Tech Stack](architecture/TECH_STACK.md) - Technology yang digunakan
- [Design Patterns](architecture/PATTERNS.md) - Design patterns & best practices

### 📝 Contributing

- [Contributing Guide](CONTRIBUTING.md) - Cara berkontribusi
- [Code Style](CODE_STYLE.md) - Style guide & conventions
- [Testing Guide](TESTING.md) - Panduan testing

---

## 🚀 Quick Start untuk Contributor

### 1. Setup Development Environment

```bash
# Clone repository
git clone <repo-url>
cd Backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup database
flask db upgrade

# Create admin user
python create_admin.py

# Run server
python main.py
```

### 2. Baca Dokumentasi

1. Mulai dengan [Project Structure](architecture/PROJECT_STRUCTURE.md)
2. Pelajari [Auth System](auth/README.md)
3. Ikuti [Developer Guide](auth/DEVELOPER_GUIDE.md)
4. Baca [Contributing Guide](CONTRIBUTING.md)

### 3. Testing

```bash
# Quick test
python test_quick.py

# Full test suite
python test_auth.py

# Run specific test
pytest tests/test_auth.py
```

---

## 🎯 Fokus Area untuk Contributor

### 🔥 High Priority

- [ ] Email service integration (password reset)
- [ ] Rate limiting implementation
- [ ] Image processing endpoints
- [ ] File upload & storage

### 📊 Medium Priority

- [ ] User profile management
- [ ] Admin dashboard
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Logging & monitoring

### 💡 Nice to Have

- [ ] 2FA (Two-Factor Authentication)
- [ ] OAuth integration (Google, GitHub)
- [ ] Webhook notifications
- [ ] Usage analytics

---

## 📞 Bantuan & Support

- **Issues:** Buat issue di GitHub repository
- **Discussions:** Gunakan GitHub Discussions untuk pertanyaan
- **Code Review:** Submit PR dan tunggu review dari maintainer

---

## 📖 Resource Tambahan

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)

---

**Happy Contributing! 🎉**
