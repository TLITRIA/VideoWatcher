"""重建数据库的任务"""

import os, sys
import traceback
import random
import shutil

# from Common.Process import *
from Common.Logger import *
from Common.Abspath import *
from Common.Process import *
from Web.MyWebDriver import *
from Web.biliParse import *
from Web.ytbParse import *
from DataAccess.DataBase import *
from DataAccess.sql_bilibili import *
from DataAccess.sql_ytb import *


def task_rebuild_bilibili(db_fp: str):
    """重建bilibili数据库"""
    l = Logger()
    db = DataBase()
    if db.isConnected:
        db.Disconnect()
    db.Connect(db_fp)
    create_all(db, default_create_sqls)
    up_ids = []
    df = get_whole_table(db, "up")
    df = df.sort_values(by="data_time")
    l.info(f"bilibili原数据{len(df)}条")
    results: dict = {}
    for i in range(len(df)):
        up_id = str(df.loc[i, "up_id"])
        ret, enum = judge_bilibiliUP_needupdate(db, up_id)
        results[enum.name] = results.get(enum.name, 0) + 1
        if enum.value > 0:
            up_ids.append(up_id)
        if enum == BiliEnum.UpNeedDeleteALL:
            delete_up(db, up_id)
    l.info(f"bilibili - 筛选后的数据{len(up_ids)}条")
    l.info(f"bilibili数据库统计：{str(results)}")
    urls = [f"https://space.bilibili.com/{x}/upload/video" for x in up_ids]
    random.shuffle(urls)
    with timeblock("BiliBili") as tb:
        l.info("开始重建BiliBili数据库")
        try:
            task_bili_update_all(urls, db_fp, True)
        finally:
            db.Disconnect()
            MyWebDriver().Quit()
    l.info(f"重建BiliBili数据库耗时{generate_duration_string(int(tb['elapsed']))}")


def task_rebuild_youtube(db_fp: str):
    """重建youtube数据库"""
    l = Logger()
    db = DataBase()
    if db.isConnected:
        db.Disconnect()
    db.Connect(db_fp)
    create_all(db, ytb_create_sqls)
    up_ids = []
    df = get_whole_table(db, "ytbup")
    df = df.sort_values(by="data_time")
    l.info(f"youtube原数据{len(df)}条")
    results: dict = {}
    for i in range(len(df)):
        up_id = str(df.loc[i, "up_id"])
        ret, enum = judge_ytbUp_needupdate(db, up_id)
        results[enum.name] = results.get(enum.name, 0) + 1
        if enum.value > 0:
            up_ids.append(up_id)
    l.info(f"ytb - 筛选后的数据{len(up_ids)}条")
    l.info(f"ytb数据库统计：{str(results)}")
    urls = [f"https://www.youtube.com/@{x}/" for x in up_ids]
    random.shuffle(urls)

    with timeblock("Youtube") as tb:
        l.info("开始重建Youtube数据库")
        try:
            task_update_ytb_database(urls, db_fp)
        finally:
            db.Disconnect()
            MyWebDriver().Quit()
    l.info(f"重建Youtube数据库耗时{generate_duration_string(int(tb['elapsed']))}")


if __name__ == "__main__":
    pm = ProcessManager()
    pm.StartWorkers(2)
    l = Logger()
    l.info(logStart())

    db = DataBase()
    db.Connect()
    create_all(db, default_create_sqls)
    create_all(db, ytb_create_sqls)
    db.Disconnect()
    # ==================================== #
    # 备份
    bkpath = generate_zip_filepath(default_db_fp)
    if not os.path.exists(bkpath):  # 保证备份不会因为重复执行而反复覆盖
        create_zip(default_db_fp, bkpath)
        l.info(f"备份完成，备份文件为{bkpath}")
    # 重建
    pm.AddTask(task_rebuild_bilibili, *[default_db_fp])
    pm.AddTask(task_rebuild_youtube, *[default_db_fp])
    # ==================================== #
    pm.WaitAll()
    db.Disconnect()
    l.info(logEnd())
