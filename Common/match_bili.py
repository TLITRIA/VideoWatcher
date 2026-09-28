import re
from Common.Logger import *

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


def parse_upload_timestamp(
    upload_string: str,
) -> int:
    ret = -1
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    match = re.match(r"(\d+)天前", upload_string)
    if match:
        return get_timestamp() - int(match.group(1)) * 24 * 60 * 60
    match = re.match(r"昨天 (\d+):(\d+)", upload_string)
    if match:  # timestamp 计时起点是1970年1月1日8:00:00
        return (
            (get_timestamp() // (24 * 60 * 60) - 1) * 24 * 60 * 60
            - 8 * 60 * 60
            + int(match.group(1)) * 60 * 60
            + int(match.group(2)) * 60
        )
    match = re.match(r"(\d+)小时前", upload_string)
    if match:
        return get_timestamp() - int(match.group(1)) * 60 * 60
    match = re.match(r"(\d+)分钟前", upload_string)
    if match:
        return get_timestamp() - int(match.group(1)) * 60
    match = re.match(r"(\d+)月(\d+)日", upload_string)
    if match:
        return get_timestamp_bydate(year, int(match.group(1)), int(match.group(2)))
    match = re.match(r"(\d+)年(\d+)月(\d+)日", upload_string)
    if match:
        return get_timestamp_bydate(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    match = re.match(r"(\d+)-(\d+)-(\d+)", upload_string)
    if match:
        return get_timestamp_bydate(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    match = re.match(r"(\d+)-(\d+)", upload_string)
    if match:
        return get_timestamp_bydate(year, int(match.group(1)), int(match.group(2)))
    if upload_string == "昨天":
        return get_timestamp_bydate(year, month, day) - 24 * 60 * 60
    if ret == -1:
        print("-" * 80)
        print(upload_string)
        raise Exception(f"无法解析上传时间戳: {upload_string}")
    return ret
