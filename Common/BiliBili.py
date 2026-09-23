import re

"""
有关BiliBili的匹配
"""


def match_upspace(url: str) -> str | None:
    match = re.match(r"https://space.bilibili.com/([0-9]*)/upload/video", url)
    if match:
        return match.group(1)
    else:
        return None


def match_video(url: str) -> str | None:
    match = re.match(r"https://www.bilibili.com/video/([0-9a-zA-Z]*).*", url)
    if match:
        return match.group(1)
    else:
        return None


def match_playlist(url: str) -> list[str] | None:
    match = re.match(
        r"https://space.bilibili.com/([0-9]*)/favlist\?fid=([0-9]*)&ftype=create",
        url,
    )
    if match:
        return [match.group(1), match.group(2)]
    else:
        return None
