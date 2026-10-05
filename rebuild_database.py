"""重建数据库的任务"""

import os, sys
import traceback
import random
import shutil

# from Common.Process import *
from Common.Logger import *
from Common.Abspath import *
from Web.MyWebDriver import *
from Web.biliParse import *
from Web.ytbParse import *
from DataAccess.DataBase import *
from DataAccess.sql_bilibili import *
from DataAccess.sql_ytb import *


def rebuild_bilibili(db: DataBase, db_fp: str):
    """重建bilibili数据库"""
    if db.isConnected:
        db.Disconnect()
    db.Connect(db_fp)
    create_all(db, default_create_sqls)
    up_ids = []
    df = get_whole_table(db, "up")
    df = df.sort_values(by="data_time")
    l.info(f"bilibili原数据{len(df)}条")
    c1 = 0
    c2 = 0
    c3 = 0
    for i in range(len(df)):
        ret = judge_bilibiliUP_needupdate(db, str(df.loc[i, "up_id"]))
        if ret != 0:
            up_ids.append(str(df.loc[i, "up_id"]))
        if ret == 1:
            c1 += 1
        if ret == 2:
            c2 += 1
        if ret == 3:
            c3 += 1
    l.info(f"筛选后的数据{len(up_ids)}条")
    l.info(f"up数据已过期24小时的有{c1}条")
    l.info(f"视频与数据库中相差过大的有{c2}条")
    l.info(f"最新的视频不在数据库中的有{c3}条")
    urls = [f"https://space.bilibili.com/{x}/upload/video" for x in up_ids]
    random.shuffle(urls)
    task_bili_update_all(urls, db_fp, True)


def rebuild_youtube(db: DataBase, db_fp: str):
    """重建youtube数据库"""
    if db.isConnected:
        db.Disconnect()
    db.Connect(db_fp)
    create_all(db, ytb_create_sqls)
    up_ids = []
    df = get_whole_table(db, "ytbup")
    df = df.sort_values(by="data_time")
    l.info(f"youtube原数据{len(df)}条")
    for i in range(len(df)):
        if judge_ytbUp_needupdate(db, str(df.loc[i, "up_id"])):
            up_ids.append(str(df.loc[i, "up_id"]))
    l.info(f"筛选后的数据{len(up_ids)}条")
    urls = [f"https://www.youtube.com/@{x}/" for x in up_ids]
    random.shuffle(urls)
    task_update_ytb_database(urls, db_fp)


if __name__ == "__main__":
    l = Logger()
    l.info(logStart())
    # ==================================== #
    db = DataBase()
    db.Connect()
    create_all(db, default_create_sqls)
    create_all(db, ytb_create_sqls)
    db.Disconnect()
    bkpath = generate_zip_filepath(default_db_fp)
    if not os.path.exists(bkpath):  # 保证备份不会因为重复执行而反复覆盖
        create_zip(default_db_fp, bkpath)
        l.info(f"备份完成，备份文件为{bkpath}")
    # ==================================== #
    # BiliBili
    with timeblock("BiliBili") as tb:
        l.info("开始重建BiliBili数据库")
        rebuild_bilibili(db, default_db_fp)
    l.info(f"重建BiliBili数据库耗时{generate_duration_string(int(tb['elapsed']))}")

    # ==================================== #
    # Ytb
    with timeblock("Youtube") as tb:
        l.info("开始重建Youtube数据库")
        rebuild_youtube(db, default_db_fp)
    l.info(f"重建Youtube数据库耗时{generate_duration_string(int(tb['elapsed']))}")
    # ==================================== #
    db.Disconnect()
    l.info(logEnd())
