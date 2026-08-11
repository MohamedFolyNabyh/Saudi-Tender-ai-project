from sqlalchemy.orm import Session

from app.database.models.user import User

from app.schemas.user_schema import UserLogin

from app.core.security import (
    verify_password,
    create_access_token
)


class AuthService:

    @staticmethod
    def login(
        db: Session,
        user_data: UserLogin
    ):

        user = (
            db.query(User)
            .filter(
                User.email == user_data.email
            )
            .first()
        )

        if not user:
            raise ValueError(
                "Invalid email or password"
            )

        if not verify_password(
            user_data.password,
            user.password_hash
        ):
            raise ValueError(
                "Invalid email or password"
            )

        token = create_access_token(
            data={
                "sub": str(user.id)
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }