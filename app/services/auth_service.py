from sqlalchemy.orm import Session

from app.auth.password import hash_password, verify_password
from app.models.user import User


def register_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    role: str = "doctor"
):
    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        return None

    new_user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=role,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def authenticate_user(
    db: Session,
    email: str,
    password: str
):
    user = db.query(User).filter(
        User.email == email
    ).first()

    if user is None:
        return None

    if not verify_password(
        password,
        user.hashed_password
    ):
        return None

    if not user.is_active:
        return None

    return user