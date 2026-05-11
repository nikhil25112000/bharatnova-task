import re


HASHTAG_PATTERN = re.compile(r"(?<!\w)#([A-Za-z0-9_]{1,50})")


def extract_hashtags(caption: str) -> list[str]:
    hashtags: list[str] = []
    seen: set[str] = set()
    for tag in HASHTAG_PATTERN.findall(caption):
        normalized = tag.lower()
        if normalized not in seen:
            seen.add(normalized)
            hashtags.append(normalized)
    return hashtags
