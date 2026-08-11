from sqlalchemy.orm import Session

from app.database.models.user import User
from app.schemas.user_schema import UserCreate
from app.core.security import hash_password


class UserService:

    @staticmethod
    def register(db: Session, user_data: UserCreate) -> User:
        # Check existing user
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("User with this email already exists.")

        # Create and save user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=hash_password(user_data.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return user