import re
import csv
from Common.Logger import *
from Common.Abspath import default_csv_fold


def match_ytb_upid(url: str) -> str:
    """解析用户id"""
    match = re.match(r"https://www.youtube.com/@([^/]*)", url)
    if match:
        return unquote(match.group(1))
    else:
        return ""


def match_ytb_videos(url: str) -> str:
    """匹配youtube视频发布页"""
    match = re.match(r"https://www.youtube.com/@([^/]*)/videos", url)
    if match:
        return match.group(1)
    else:
        return ""


def match_ytb_streams(url: str) -> str:
    """匹配youtube直播发布页"""
    match = re.match(r"https://www.youtube.com/@([^/]*)/streams", url)
    if match:
        return match.group(1)
    else:
        return ""

def match_ytb_shorts(url: str) -> str:
    """匹配youtube shorts发布页"""
    match = re.match(r"https://www.youtube.com/@([^/]*)/shorts", url)
    if match:
        return match.group(1)
    else:
        return ""


def match_ytb_vid_byUrl(url: str) -> str:
    """匹配youtube视频id"""
    match = re.match(r"https://www.youtube.com/watch\?v=([^&]*)", url)
    if match:
        return match.group(1)
    else:
        return ""

def match_ytb_vid_byShortUrl(html: str) -> str:
    """匹配youtube短视频id"""
    match = re.search(r"https://www.youtube.com/shorts/([^&]*)", html)
    if match:
        return match.group(1)
    else:
        return ""

def parse_ytbUploadStamp(stamp: str) -> int:
    """解析youtube发布时间戳"""
    if stamp == "":
        return 0
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    ret: int = 0
    if "直播时间：" in stamp:
        stamp = stamp.replace("直播时间：", "")
    # ========================= #
    match = re.match(r"(\d+)小时前", stamp)
    if match:
        return get_timestamp() - int(match.group(1)) * 60 * 60
    match = re.match(r"(\d+)天前", stamp)
    if match:
        return get_timestamp_bydate(year, month, day) - int(match.group(1)) * 24 * 60 * 60
    match = re.match(r"(\d+)周前", stamp)
    if match:
        return get_timestamp_bydate(year, month, day) - int(match.group(1)) * 7 * 24 * 60 * 60
    match = re.match(r"(\d+)个月前", stamp)
    if match:
        offset = int(match.group(1))
        while month - offset < 1:
            offset -= month
            month = 12
            year -= 1
        month -= offset
        return get_timestamp_bydate(year, month, 1)
    match = re.match(r"(\d+)年前", stamp)
    if match:
        return get_timestamp_bydate(year - int(match.group(1)), 1, 1)
        print(mid_mess("检查解析结果"))
        print(stamp)
        print(datetime.fromtimestamp(ret))
        print("-" * 80)
    # ========================= #
    if ret == 0:
        fp = os.path.join(default_csv_fold, "ytb_uploadstamp.csv")
        if not os.path.exists(fp):
            g_mkdir_byfp(fp)
            with open(fp, "w", encoding="utf-8") as f:
                """"""
        with open(fp, "a+", encoding="utf-8") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow([stamp])
        print(mid_mess(f"无法解析的timestamp：{stamp}"))
    else:
        """"""
    return ret


def parse_ytbPlaytimes(playstring: str) -> int:
    """解析youtube播放次数"""
    if playstring == "":
        return 0
    ret: int = -1
    # ========================= #
    try:
        ret = int(playstring)
        return ret
    except:
        pass
    match = re.match(r"([\.\d]*)万", playstring)
    if match:
        return int(float(match.group(1)) * 10000)
        print(mid_mess("检查解析结果"))
        print(playstring)
        print(ret)
        print("-" * 80)
    # ========================= #
    if ret == -1:
        fp = os.path.join(default_csv_fold, "ytb_playtimes.csv")
        if not os.path.exists(fp):
            g_mkdir_byfp(fp)
            with open(fp, "w", encoding="utf-8") as f:
                """"""
        with open(fp, "a+", encoding="utf-8") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow([playstring])
        # print(mid_mess(f"无法解析的play：{playstring}"))
    else:
        """"""
    return ret


def parse_ytbDuration(duration: str) -> int:
    """解析youtube视频时长"""
    if duration == "":
        return 0
    ret: int = -1
    # ========================= #
    if duration in ["即将开始", "直播"]:
        ret = 0
    match = re.match(r"(\d+):(\d+):(\d+)", duration)
    if match:
        return int(match.group(1)) * 3600 + int(match.group(2)) * 60 + int(match.group(3))
    match = re.match(r"(\d+):(\d+)", duration)
    if match:
        return int(match.group(1)) * 60 + int(match.group(2))
    if ret == -1:
        fp = os.path.join(default_csv_fold, "ytb_duration.csv")
        if not os.path.exists(fp):
            g_mkdir_byfp(fp)
            with open(fp, "w", encoding="utf-8") as f:
                """"""
        with open(fp, "a+", encoding="utf-8") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow([duration])
        # print(mid_mess(f"无法解析的duration：{duration}"))
    else:
        """"""
    return ret
