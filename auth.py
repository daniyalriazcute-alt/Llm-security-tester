"""Registration + login with bcrypt."""
import bcrypt
from database import create_user, get_user_by_email


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def register_user(name: str, email: str, password: str):
    if not name or not email or not password:
        return False, "All fields are required."
    if "@" not in email or "." not in email:
        return False, "Enter a valid email address."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if get_user_by_email(email):
        return False, "An account with this email already exists."
    ok = create_user(name, email, hash_password(password))
    return (True, "Account created. Please sign in.") if ok else (False, "Could not create account.")


def login_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return None, "No account found with this email."
    if not verify_password(password, user["password_hash"]):
        return None, "Incorrect password."
    return user, None
