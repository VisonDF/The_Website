from werkzeug.security import generate_password_hash

from app import create_app   # adjust if your factory name differs
from db import db
from models.admin_user import AdminUser

USERNAME = "admin"
NEW_PASSWORD = "CHANGE_ME_NOW"


def main():
    app = create_app()

    with app.app_context():
        user = AdminUser.query.filter_by(username=USERNAME).first()

        if user is None:
            print(f"Creating admin user '{USERNAME}'")
            user = AdminUser(username=USERNAME)
            db.session.add(user)
        else:
            print(f"Updating password for '{USERNAME}'")

        user.password_hash = generate_password_hash(NEW_PASSWORD)
        db.session.commit()

        print("✅ Password updated successfully")


if __name__ == "__main__":
    main()
