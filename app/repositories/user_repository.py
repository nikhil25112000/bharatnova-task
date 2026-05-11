from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, *, username: str, email: str) -> User:
        user = User(username=username, email=email)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, *, username: str, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(or_(User.username == username, User.email == email))
        )
        return result.scalar_one_or_none()
