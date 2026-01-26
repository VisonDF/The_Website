from werkzeug.security import generate_password_hash
from app import create_app
from db import db
from models.admin_user import AdminUser

USERNAME = "admin"
NEW_PASSWORD = "1234"   # 🔴 change this

def main():
    app = create_app()

    with app.app_context():
        user = AdminUser.query.filter_by(username=USERNAME).first()

        password_hash = generate_password_hash(NEW_PASSWORD)

        if user:
            user.password_hash = password_hash
            print(f"Updated password for user '{USERNAME}'")
        else:
            user = AdminUser(
                username=USERNAME,
                password_hash=password_hash
            )
            db.session.add(user)
            print(f"Created user '{USERNAME}'")

        db.session.commit()
        print("✔ Password hash:", password_hash)

if __name__ == "__main__":
    main()
