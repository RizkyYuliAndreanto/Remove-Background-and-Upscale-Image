from app import create_app
from app.extensions import db
from app.models.user_model import User

app = create_app()
def create_super_admin():
    with app.app_context():
        email = input("Enter super admin email: ")
        password = input("Enter super admin password: ")

        if User.query.filter_by(email=email).first():
            print("User with this email already exists.")
            return
        
        admin = User(email=email,role='admin',is_activate_status=True)
        admin.set_password(password)
        admin.generate_api_key()

        db.session.add(admin)
        db.session.commit()

        print(f"Super admin created with email: {email}")
        print(f"API Key: {admin.api_key}")

        if __name__ =="__main__":
            create_super_admin()