import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import normalize_username
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repository = UserRepository(session)

    async def create_user(self, payload: UserCreate):
        username = normalize_username(payload.username)
        email = payload.email.lower()
        if len(username) < 3:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Username is invalid")
        existing_user = await self.user_repository.get_by_username_or_email(
            username=username,
            email=email,
        )
        if existing_user:
            if existing_user.username == username:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        try:
            user = await self.user_repository.create(username=username, email=email)
            await self.session.commit()
            return user
        except IntegrityError as exc:
            await self.session.rollback()
            logger.exception("User creation failed due to integrity error")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists") from exc
        except SQLAlchemyError as exc:
            await self.session.rollback()
            logger.exception("User creation failed due to database error")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable") from exc

    async def get_user(self, user_id: UUID):
        try:
            user = await self.user_repository.get_by_id(user_id)
        except SQLAlchemyError as exc:
            logger.exception("User lookup failed")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable") from exc
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
