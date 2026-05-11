import logging

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ProgrammingError

from app.db.base import Base
from app.db.session import engine
from app.models import Post, User  # noqa: F401

logger = logging.getLogger(__name__)


def _build_admin_url(database_url: str) -> tuple[URL, str]:
    parsed = make_url(database_url)
    target_database = parsed.database
    admin_database = "postgres" if target_database != "postgres" else "template1"
    sync_driver = parsed.drivername.replace("+asyncpg", "+psycopg2")
    admin_url = parsed.set(drivername=sync_driver, database=admin_database)
    return admin_url, target_database


def ensure_database_exists() -> None:
    admin_url, target_database = _build_admin_url(engine.url.render_as_string(hide_password=False))
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", pool_pre_ping=True)
    try:
        with admin_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
                {"database_name": target_database},
            ).scalar()
            if not exists:
                connection.execute(text(f'CREATE DATABASE "{target_database}"'))
                logger.info("Database created: %s", target_database)
    except ProgrammingError:
        logger.exception("Failed while ensuring database exists")
        raise
    finally:
        admin_engine.dispose()


async def verify_database_connection() -> None:
    async with engine.begin() as connection:
        await connection.execute(text("SELECT 1"))
    logger.info("Database connection verified")


async def initialize_database() -> None:
    ensure_database_exists()
    await verify_database_connection()
    async with engine.begin() as connection:
        await connection.execute(text("DROP INDEX IF EXISTS ix_posts_created_at"))
        await connection.execute(text("DROP INDEX IF EXISTS ix_posts_hashtags_gin"))
        await connection.execute(text("DROP INDEX IF EXISTS ix_posts_search_vector_gin"))
        await connection.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")
