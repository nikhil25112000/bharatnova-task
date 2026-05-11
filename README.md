# Social Feed & Media Metadata Microservice

Production-grade FastAPI microservice for user management, social feed posts, trending feeds, PostgreSQL full-text search, Redis caching, and upload metadata generation.

## Features

- Async FastAPI service with SQLAlchemy 2.0 and `asyncpg`
- PostgreSQL-backed user and post management
- Redis caching for trending posts with graceful fallback
- Full-text search using PostgreSQL `tsvector` and GIN index
- Cursor-based pagination for infinite scroll feeds
- Upload URL generation with validation
- Structured JSON logging and centralized exception handling
- Pytest coverage for key endpoints

## Architecture

The service follows a layered structure:

- `api`: FastAPI routes and dependency injection
- `services`: Business logic and orchestration
- `repositories`: Database access
- `models`: SQLAlchemy ORM entities
- `schemas`: Request and response validation
- `core`: Configuration, logging, security, Redis wiring, constants
- `middleware`: Error handling and upload validation
- `utils`: Cursor pagination, hashtag parsing, S3 helpers

This separation keeps database concerns, transport concerns, and business logic isolated and interview-ready.

## Project Structure

```text
social-feed-microservice/
├── app/
├── requirements.txt
├── .env.example
├── README.md
├── postman_collection.json
```

## Environment Variables

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Important variables:

- `DATABASE_URL`: Async SQLAlchemy PostgreSQL URL
- `REDIS_URL`: Redis connection string
- `UPLOAD_URL_EXPIRY_SECONDS`
- `UPLOAD_BASE_URL`
- `UPLOAD_MAX_FILE_SIZE_BYTES`

## Local Setup

1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure `.env`.
4. Start the API:

```bash
uvicorn app.main:app --reload
```

Swagger UI is available at `http://localhost:8000/docs`.

## Database Schema

### `users`

- `id` UUID primary key
- `username` unique
- `email` unique
- `created_at`

### `posts`

- `id` UUID primary key
- `user_id` foreign key
- `caption`
- `media_url`
- `bitrate_status`
- `hashtags` text array
- `created_at`
- `search_vector` generated tsvector column

## API Endpoints

### Users

- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{user_id}` - Get user by ID

### Posts

- `POST /api/v1/posts` - Create post
- `GET /api/v1/posts` - List posts with cursor pagination
- `GET /api/v1/posts/{post_id}` - Get post by ID
- `DELETE /api/v1/posts/{post_id}` - Delete post

### Feed Discovery

- `GET /api/v1/trending` - Get top trending posts
- `GET /api/v1/search?query=...` - Search posts

### Uploads

- `POST /api/v1/upload/presigned-url` - Generate upload URL metadata

### Health

- `GET /health`

## Response Format

Success:

```json
{
  "success": true,
  "message": "something",
  "data": {}
}
```

Error:

```json
{
  "success": false,
  "message": "error message"
}
```

## Pagination

The posts feed uses cursor pagination optimized for infinite scroll:

- Request: `GET /api/v1/posts?cursor=<opaque_cursor>&limit=10`
- Ordering: `created_at DESC, id DESC`
- Response includes `next_cursor`

The cursor is base64-encoded JSON containing `created_at` and `id`, which avoids offset-scan performance issues on large tables.

## Search

Search uses PostgreSQL full-text search:

- Generated `tsvector` column on `posts`
- GIN index on `search_vector`
- Sanitized query input
- Ranked ordering using `ts_rank_cd`

This design is significantly more scalable than naive `ILIKE` scans.

## Trending Logic

`GET /api/v1/trending` returns the top 10 posts based on:

- Priority hashtags: `#viral`, `#trending`, `#fyp`
- Then recency

Redis behavior:

- Cached under a single key for 5 minutes
- If Redis is unavailable, the endpoint still works by falling back to PostgreSQL

## Upload Flow

1. Client calls `POST /api/v1/upload/presigned-url`
2. Backend validates filename, extension, and size
3. Backend generates upload metadata for the file path
4. Backend returns:
   - `upload_url`
   - `file_url`
   - `expires_in`

Allowed extensions:

- `.mp4`
- `.m3u8`

Maximum size:

- `100MB`

## Validation and Edge Cases

Handled cases include:

- Invalid UUIDs
- Duplicate usernames and emails
- Missing users and posts
- Empty or oversized captions
- Invalid media URLs
- Invalid or malformed pagination cursors
- Empty search queries
- Unsupported upload extensions
- Oversized uploads
- Redis failures with DB fallback
- Database failures with proper HTTP 503
- Transaction rollback on write errors
- Hashtag extraction and normalization

## Logging

The service logs:

- Request method, path, status code, and latency
- Redis failures
- Database failures
- Upload metadata generation events
- Unhandled exceptions

Logs are emitted as structured JSON for production observability pipelines.

## Testing

Run tests:

```bash
pytest app/tests -q
```

Covered scenarios:

- Create post
- Delete post
- Search endpoint
- Trending endpoint
- Upload validation

## Postman

Import `postman_collection.json` into Postman and set `base_url` to your target environment.

## Notes for Production

- Restrict `ALLOWED_ORIGINS` to trusted domains
- Use managed PostgreSQL and Redis with TLS where required
- Add authentication and authorization if the service becomes multi-tenant
- Add rate limiting middleware using the existing request-key preparation pattern
