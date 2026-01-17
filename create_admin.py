print("--- Script Starting ---") # Debugging 1

from app import create_app
from app.extensions import db
from app.models.user_model import User

app = create_app()

def create_super_admin():
    print("--- Function Called ---") # Debugging 2
    with app.app_context():
        # Input Data
        email = input("Masukkan Email Admin: ")
        password = input("Masukkan Password Admin: ")
        
        # Validasi
        if not email or not password:
            print("❌ Error: Email dan Password tidak boleh kosong.")
            return

        # Cek apakah user sudah ada
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"⚠️ User {email} sudah ada di database!")
            return

        # Buat Admin Baru
        try:
            admin = User(email=email, role='admin', is_active_status=True)
            admin.set_password(password)
            admin.generate_api_key()
            
            db.session.add(admin)
            db.session.commit()
            
            print("---------------------------------------")
            print(f"✅ SUKSES! Admin dibuat: {email}")
            print(f"🔑 API Key Admin: {admin.api_key}")
            print("---------------------------------------")
        except Exception as e:
            print(f"❌ Terjadi Error: {e}")

# --- BAGIAN INI SANGAT PENTING ---
# Pastikan if __name__ sejajar dengan def (tidak menjorok ke dalam)
if __name__ == "__main__":
    create_super_admin()