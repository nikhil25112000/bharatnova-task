from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, case, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import TRENDING_HASHTAGS
from app.models.post import Post


class PostRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: UUID,
        caption: str,
        media_url: str,
        bitrate_status: str,
        hashtags: list[str],
    ) -> Post:
        post = Post(
            user_id=user_id,
            caption=caption,
            media_url=media_url,
            bitrate_status=bitrate_status,
            hashtags=hashtags,
        )
        self.session.add(post)
        await self.session.flush()
        await self.session.refresh(post)
        return post

    async def get_by_id(self, post_id: UUID) -> Post | None:
        result = await self.session.execute(select(Post).where(Post.id == post_id))
        return result.scalar_one_or_none()

    async def delete(self, post: Post) -> None:
        await self.session.delete(post)

    async def list_posts(
        self,
        *,
        limit: int,
        cursor_created_at: datetime | None = None,
        cursor_post_id: UUID | None = None,
    ) -> list[Post]:
        query = select(Post).order_by(desc(Post.created_at), desc(Post.id)).limit(limit + 1)
        if cursor_created_at and cursor_post_id:
            query = query.where(
                or_(
                    Post.created_at < cursor_created_at,
                    and_(Post.created_at == cursor_created_at, Post.id < cursor_post_id),
                )
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_trending_posts(self, limit: int) -> list[Post]:
        hashtag_score = (
            case((Post.hashtags.any(TRENDING_HASHTAGS[0]), 3), else_=0)
            + case((Post.hashtags.any(TRENDING_HASHTAGS[1]), 2), else_=0)
            + case((Post.hashtags.any(TRENDING_HASHTAGS[2]), 1), else_=0)
        ).label("score")

        result = await self.session.execute(
            select(Post).order_by(desc(hashtag_score), desc(Post.created_at)).limit(limit)
        )
        return list(result.scalars().all())

    async def search_posts(self, query_text: str, limit: int) -> list[Post]:
        dialect_name = self.session.bind.dialect.name if self.session.bind else "unknown"
        if dialect_name == "postgresql":
            ts_query = func.plainto_tsquery("simple", query_text)
            search_vector = func.to_tsvector(
                "simple",
                func.coalesce(Post.caption, "") + " " + func.array_to_string(func.coalesce(Post.hashtags, "{}"), " "),
            )
            rank = func.ts_rank_cd(search_vector, ts_query).label("rank")
            result = await self.session.execute(
                select(Post)
                .where(search_vector.op("@@")(ts_query))
                .order_by(desc(rank), desc(Post.created_at))
                .limit(limit)
            )
            return list(result.scalars().all())

        fallback = await self.session.execute(
            select(Post)
            .where(
                or_(
                    Post.caption.ilike(f"%{query_text}%"),
                    func.lower(func.array_to_string(Post.hashtags, " ")).ilike(f"%{query_text.lower()}%"),
                )
            )
            .order_by(desc(Post.created_at))
            .limit(limit)
        )
        return list(fallback.scalars().all())
