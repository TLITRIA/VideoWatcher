import os
import time
import logging
from datetime import datetime, timedelta
from contextlib import contextmanager
from Pattern.singleton import singleton
from Common.Common import *
from Common.Abspath import default_log_fp

@contextmanager
def timeblock(label:str=""):
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        print(f"{label} 耗时： {end - start:.6f} s")
        # TODO 记录label/代码位置/运行频率/平均耗时，形成表格记录

def mid_mess(mess:str, fillchar:str='='):
    if len(fillchar) != 1:
        fillchar = "="
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
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        if not os.path.exists(log_fp):
            g_mkdir_byfp(log_fp)
            with open(log_fp, 'w') as f:
                pass
        if os.path.exists(log_fp) and os.path.isfile(log_fp):
            file_handler = logging.FileHandler(log_fp, mode='a')
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

def get_timestamp()->int:
    return int(time.time())