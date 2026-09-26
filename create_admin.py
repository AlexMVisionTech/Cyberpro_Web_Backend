"""Create or update an administrator account without exposing its password in shell history."""

from getpass import getpass

import auth
import models
from database import SessionLocal, engine


def main() -> None:
    username = input("Admin email: ").strip().lower()
    if not username:
        raise SystemExit("Admin email is required.")
    if not username.endswith("@cyberpro.ke"):
        raise SystemExit("Only @cyberpro.ke administrator emails are allowed.")

    password = getpass("Admin password: ")
    confirm = getpass("Confirm password: ")
    if len(password) < 12:
        raise SystemExit("Use a password with at least 12 characters.")
    if password != confirm:
        raise SystemExit("Passwords do not match.")

    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(models.AdminUser).filter_by(username=username).first()
        if admin is None:
            admin = models.AdminUser(username=username)
            db.add(admin)
        admin.hashed_password = auth.hash_password(password)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(f"Administrator account ready: {username}")


if __name__ == "__main__":
    main()
