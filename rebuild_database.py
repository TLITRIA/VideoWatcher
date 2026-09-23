"""重建数据库的任务"""

import os, sys
import traceback
from Common.Logger import *
from Common.Abspath import *
from Web.MyWebDriver import *
from Web.biliParse import *
from DataAccess.DataBase import *
from DataAccess.sql_query import *

if __name__ == "__main__":
    l = Logger()
    l.info(logStart())
    db = DataBase()
    db_fp = "D:/__Downloads__/videowatcher.db"
    db.Connect(db_fp)
    create_all(db, videowatcher_sqls)
    # ==================================== #

    urls = [
        f"https://space.bilibili.com/{x}/upload/video"
        for x in get_all_up_id(db)
    ]
    back_update_all(urls, db_fp)
    # ==================================== #

    l.info(logEnd())
    db.Disconnect()
