import re


def sanitize_title_for_filename(title: str) -> str:
    # replace any non-alpha char with '_'
    title = re.sub("[^a-zA-Z0-9]", "_", title)
    return title
