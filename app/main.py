import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.posts import router as posts_router
from app.api.routes.search import router as search_router
from app.api.routes.trending import router as trending_router
from app.api.routes.upload import router as upload_router
from app.api.routes.users import router as users_router
from app.core.config import get_settings
from app.core.constants import success_response
from app.core.logging import configure_logging
from app.core.redis import close_redis, init_redis
from app.db.init_db import initialize_database
from app.middleware.error_handler import register_exception_handlers

settings = get_settings()
configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.app_env != "test":
        await initialize_database()
        await init_redis()
    yield
    if settings.app_env != "test":
        await close_redis()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    started_at = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    logger.info(
        "request_completed method=%s path=%s status_code=%s duration_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


register_exception_handlers(app)

app.include_router(users_router, prefix=settings.api_v1_prefix)
app.include_router(posts_router, prefix=settings.api_v1_prefix)
app.include_router(upload_router, prefix=settings.api_v1_prefix)
app.include_router(trending_router, prefix=settings.api_v1_prefix)
app.include_router(search_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["Health"])
async def health_check():
    return success_response("Service is healthy", {"status": "ok"})
