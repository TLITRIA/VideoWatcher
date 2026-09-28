import os
import time
import logging
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
from Pattern.singleton import singleton
from Common.Common import *
from Common.Abspath import default_log_fp


@contextmanager
def timeblock(label: str = ""):
    start = time.perf_counter()
    result = {'elapsed':-1.0}
    try:
        yield result
    finally:
        end = time.perf_counter()
        result["elapsed"] = end - start
        print(f"{label} 耗时：{result["elapsed"]:.6f} s")
        # TODO 记录label/代码位置/运行频率/平均耗时，形成表格记录


def mid_mess(mess: str, fillchar: str = "-"):
    if len(fillchar) != 1:
        fillchar = "-"
    return f"{' ' + mess + '':{fillchar}^80}"


def logStart():
    return mid_mess(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " Program Start ")


def logEnd():
    return mid_mess(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " Program End ")


@singleton
class Logger:
    def __init__(self, log_fp: str = default_log_fp):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        if not os.path.exists(log_fp):
            g_mkdir_byfp(log_fp)
            with open(log_fp, "w") as f:
                pass
        if os.path.exists(log_fp) and os.path.isfile(log_fp):
            file_handler = logging.FileHandler(log_fp, mode="a")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)


def get_timestamp() -> int:
    return int(time.time())


def get_timestamp_bydate(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0) -> int:
    # if year is None:
    #     year = datetime.now().year
    # if month is None:
    #     month = datetime.now().month
    # if day is None:
    #     day = datetime.now().day
    dt = datetime(year, month, day, hour, minute, second)
    return int(dt.timestamp())


def update_time_require(current: int, last: int, stamplist: list) -> float:
    """TODO 报错
    估算任务完成时间
    :param current: 当前已完成任务数
    :param last: 总任务数
    :param stamplist: 记录每次完成任务的时间戳列表
    :return: 预计剩余时间（秒）
    """
    if current <= 0 or last <= 0 or current > last:
        return -1
    stamplist.append((current, get_timestamp()))
    if len(stamplist) < 2:
        return -1
    remaining_tasks = last - current
    time_per_task = (stamplist[-1][1] - stamplist[0][1]) / (stamplist[-1][0] - stamplist[0][0])
    estimated_remaining_time = float(time_per_task * remaining_tasks)
    return estimated_remaining_time


def add_timestamp_to_filename(file_path: str) -> str:
    """
    给完整文件路径的文件名添加当前时间戳后缀。
    例如：/data/report.pdf -> /data/report_20250927_153012.pdf
    """
    p = Path(file_path)
    timestamp = datetime.now().strftime("%Y%m%d")
    new_name = f"{p.stem}_{timestamp}{p.suffix}"
    return str(p.with_name(new_name))

def generate_zip_filepath(file_path: str) -> str:
    """
    生成用于保存zip文件的路径。
    例如：/data/report.pdf -> /data/report.zip
    """
    p = Path(file_path)
    timestamp = datetime.now().strftime("%Y%m%d")
    new_name = f"{p.stem}_{timestamp}.zip"
    return str(p.with_name(new_name))

def create_zip(from_path: str, to_path: str)->bool:
    """
    将单个文件压缩为zip文件。
    """
    with zipfile.ZipFile(to_path, 'w', zipfile.ZIP_LZMA) as zipf:
        zipf.write(from_path, arcname=os.path.basename(from_path))
    return os.path.exists(to_path)