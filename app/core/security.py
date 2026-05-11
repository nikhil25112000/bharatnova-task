import hashlib
import re


SEARCH_QUERY_PATTERN = re.compile(r"[^a-zA-Z0-9\s#_\-]")
USERNAME_PATTERN = re.compile(r"[^a-zA-Z0-9_.]")


def sanitize_search_query(query: str) -> str:
    cleaned = SEARCH_QUERY_PATTERN.sub(" ", query).strip()
    return " ".join(cleaned.split())


def normalize_username(username: str) -> str:
    cleaned = USERNAME_PATTERN.sub("", username.strip())
    return cleaned.lower()


def build_rate_limit_key(identifier: str, route_name: str) -> str:
    digest = hashlib.sha256(f"{identifier}:{route_name}".encode("utf-8")).hexdigest()
    return f"ratelimit:{route_name}:{digest}"
