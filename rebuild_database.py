"""重建数据库的任务"""

import os, sys
import traceback
from Common.Logger import *
from Common.Abspath import *
from Web.MyWebDriver import *
from Web.biliParse import *
from DataAccess.DataBase import *
from DataAccess.sql_query import *
from DataAccess.sql_ytb import *

if __name__ == "__main__":
    l = Logger()
    l.info(logStart())
    db = DataBase()
    # db_fp = "D:/__Downloads__/videowatcher.db"
    db_fp = default_db_fp
    db.Connect(db_fp)
    create_all(db, default_create_sqls)
    create_all(db, ytb_create_sqls)
    # ==================================== #
    # BiliBili
    up_ids = []
    df = get_all_up_info(db)
    df = df.sort_values(by="data_time")
    print(f"原数据{len(df)}条")
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
    print(f"筛选后的数据{len(up_ids)}条")
    print(f"24小时过期的数据{c1}条")
    print(f"视频总数和数据库中记录的相差过大的有{c2}条")
    print(f"最新的视频不在数据库中的有{c3}条")
    urls = [f"https://space.bilibili.com/{x}/upload/video" for x in up_ids]
    back_update_all(urls, db_fp)
    # ==================================== #

    l.info(logEnd())
    db.Disconnect()
