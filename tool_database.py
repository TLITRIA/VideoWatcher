"""处理数据库数据不完全解析的问题"""

import csv
from DataAccess.DataBase import *
from DataAccess.sql_bilibili import *
from DataAccess.sql_ytb import *
from Common.Logger import *
from Web.biliParse import *


def set_upexclude_url(db: DataBase):
    df = get_whole_table(db, "up_exclude")
    with pd.option_context(
        "display.max_columns",
        None,
        "display.width",
        None,
    ):
        print(df[["up_id", "url"]])  # 注意方括号数目
        timestamplist = []
        for i in range(len(df)):
            resttime = update_time_require(i, len(df), timestamplist)
            if i and i % 1000 == 0:
                print(f"已处理 {i} 条数据, 预计剩余时间: {resttime:.2f}s")
            df.loc[i, "url"] = f"https://space.bilibili.com/{df.loc[i, 'up_id']}/upload/video"
            update_one_up_exclude(
                db, str(df.loc[i, "up_id"]), str(df.loc[i, "reason"]), bool(df.loc[i, "yes_no"]), str(df.loc[i, "url"])
            )
        print(df[["up_id", "url"]])


def set_video_url(db: DataBase):
    df = get_whole_table(db, "video")
    with pd.option_context(
        "display.max_columns",
        None,
        "display.width",
        None,
    ):
        print(df[["v_id", "url"]])  # 注意方括号数目
        timestamplist = []
        for i in range(len(df)):
            if i and i % (len(df) // 100) == 0:
                resttime = update_time_require(i, len(df), timestamplist)
                print(f"已处理 {i} 条数据\t 预计剩余时间 {resttime:.2f}s")
            df.loc[i, "url"] = f"https://www.bilibili.com/video/{df.loc[i, 'v_id']}"
        print(df[["v_id", "url"]])
        rebuild_table(db, "video", default_create_sqls[2], df)


def upload_parse(db: DataBase):
    updf = get_whole_table(db, "up")
    updf["up_last_time"] = updf["up_last_time"].astype(int)

    with pd.option_context(
        "display.max_columns",
        None,
        "display.width",
        None,
    ):
        print(updf[["up_id", "up_last_time"]])
        print(type(updf[["up_id", "up_last_time"]].loc[0, "up_last_time"]))
        db.Disconnect()
        db.Connect()
        create_all(db, default_create_sqls)
        rebuild_table(db, "up", default_create_sqls[0], updf)


def insert_bilibili(db: DataBase):
    csv_fp = "./.cache/tmp.csv"
    upids = []
    with open(csv_fp, "r", encoding="utf-8") as f:
        csv_r = csv.reader(f)
        for row in csv_r:
            upids.append(row[0])
            insert_up_null(db, row[0], "up")
    df = get_whole_table(db, "up")
    df["url"] = "https://space.bilibili.com/" + df["up_id"] + "/upload/video"

    print(df[["up_id", "url"]])
    df.drop_duplicates(subset=["up_id"], keep="first", inplace=True)  #
    rebuild_table(db, "up", default_create_sqls[0], df)


def insert_youtube():
    db = DataBase()
    if db.isConnected:
        db.Disconnect()
    db.Connect()
    create_all(db, ytb_create_sqls)
    with open("./.cache/tmp.csv", "r", encoding="utf-8") as f:
        csv_r = csv.reader(f)
        for row in csv_r:
            insert_up_null(db, unquote(row[0]), "ytbup")
            print(unquote(row[0]))
    db.Disconnect()
