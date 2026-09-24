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

    up_ids = []

    df = get_all_up_info(db)
    df = df.sort_values(by='data_time')
    for i in range(len(df)):
        series = df.iloc[i]
        if int(series['data_time']) < get_timestamp() - 60*60*24:
            up_ids.append(series['up_id'])
            continue
        if int(series['up_sum']) == len(get_allvideoinfo_byupid(db, series['up_id'])):
            continue
        up_ids.append(series['up_id'])
    urls = [f"https://space.bilibili.com/{x}/upload/video" for x in up_ids]
    print(f"共计 {len(urls)} 个b站Up需要更新数据")
    back_update_all(urls, db_fp)
    # ==================================== #

    l.info(logEnd())
    db.Disconnect()
