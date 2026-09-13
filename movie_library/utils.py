import re

YOUTUBE_PATTERN = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([\w-]{11})"
)


def youtube_embed_url(url: str | None) -> str | None:
    if not url:
        return None
    match = YOUTUBE_PATTERN.search(url)
    if not match:
        return None
    return f"https://www.youtube.com/embed/{match.group(1)}"
