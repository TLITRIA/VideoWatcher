"""youtube dlc 扩充"""
from DataAccess.sql_bilibili import *

ytb_create_sqls = [
    """
CREATE TABLE IF NOT EXISTS ytbup(
    up_id TEXT, -- up主id 值得注意的是油管id已经很有辨识度了
    up_name TEXT, -- up主名称
    intro TEXT, -- 简介
    url TEXT, -- 前往主页
    face TEXT, -- up主头像
    data_time INT, -- up自身数据更新时间
    tag_time INT, -- tag更新时间
    latest_video_id TEXT, -- 最新视频id
    latest_stream_id TEXT, -- 最新直播id
    last_update_video_time INT, -- up视频数据更新时间
    PRIMARY KEY (up_id)
);""",
    """
CREATE TABLE IF NOT EXISTS ytbup_tag(
    up_id TEXT NOT NULL, -- up主id号
    tag TEXT NOT NULL, -- tag标签
    PRIMARY KEY (up_id, tag)
);""",
    """
CREATE TABLE IF NOT EXISTS ytbvideo( 
    v_id TEXT, -- 视频id
    up_id TEXT, -- up主id
    ytbtype INT, -- 类型：0 其他/默认 1 视频 2 直播
    title TEXT, -- 视频标题
    url TEXT, -- 前往视频页
    cover TEXT, -- 视频封面链接
    upload INT, -- 视频上传时间
    play INT, -- 播放量
    duration INT, -- 视频时长
    isCharge INT, -- 视频是否付费
    data_time INT, -- 数据更新时间
    tag_time INT, -- tag更新时间
    PRIMARY KEY (v_id)
);""",
    # 注意该表存放的是广义上的视频：直播/短视频/视频都视为视频
    # 不搞视频tag表，而是在浏览时直接下载
    # 不搞排除表
]


# ============================================================ #
def ytb_insert_up_null(db: DataBase, up_id: str):
    insert_up_null(db, up_id, "ytbup")


def ytb_insert_up(db: DataBase, df: pd.DataFrame):
    insert_up(db, df, "ytbup")


def ytb_insert_video(db: DataBase, df: pd.DataFrame):
    insert_video(db, df, "ytbvideo")


def ytb_insert_up_tag(db: DataBase, up_id: str, tag: str):
    insert_up_tag(db, up_id, tag, "ytbup_tag")


# ============================================================ #
def ytb_delete_up_tag(db: DataBase, up_id: str, tag: str):
    delete_up_tag(db, up_id, tag, "ytbup_tag")


# ============================================================ #
def ytb_update_up_tagtime(db: DataBase, up_id: str):
    update_up_tagtime(db, up_id, "ytbup")


# ============================================================ #
def ytb_get_up_info(db: DataBase, up_id: str) -> pd.DataFrame:
    return get_up_info(db, up_id, "ytbup")


def ytb_get_video_info(db: DataBase, v_id: str) -> pd.DataFrame:
    return get_video_info(db, v_id, "ytbvideo")


def ytb_get_up_selectedtags(db: DataBase, up_id: str) -> list:
    return get_up_selectedtags(db, up_id, "ytbup_tag")


def ytb_get_up_unselectedtags(db: DataBase, up_id: str) -> list:
    return get_up_unselectedtags(db, up_id, "ytbup_tag")


def ytb_get_up_unfilled(db: DataBase) -> list:
    ret = []
    if not db.isConnected:
        return []
    sql = (
        "SELECT up_id FROM ytbup WHERE "
        "up_name IS NULL "
        "OR intro IS NULL "
        "OR face IS NULL "
        "OR data_time IS NULL "
        # "OR latest_video_id IS NULL " # 为空是正常的
        # "OR latest_stream_id IS NULL " # 为空是正常的
        "OR last_update_video_time IS NULL;"
    )
    ret = [row[0] for row in db.conn.execute(sql).fetchall() if row[0] != ""]
    ret = sorted(list(set(ret)))
    return ret


def ytb_get_allvideoinfo_byupid(db: DataBase, up_id: str) -> pd.DataFrame:
    return get_allvideoinfo_byupid(db, up_id)


def judge_ytbUp_needupdate(db: DataBase, up_id: str) -> bool:
    df = ytb_get_up_info(db, up_id)
    if len(df) != 1:
        return False
    series = df.iloc[0]
    if series["up_id"] in ytb_get_up_unfilled(db):
        return True
    if not series["data_time"] or int(series["data_time"]) < get_timestamp() - 60 * 60 * 24:  # 24h未更新
        return True
    if (
        not series["last_update_video_time"]
        or int(series["last_update_video_time"]) < get_timestamp() - 60 * 60 * 24 * 7
    ):  # 7d未下载
        return True
    df = get_allvideoinfo_byupid(db, up_id, "ytbup")
    if df.empty:
        return True  # 没有视频 不会关注一个没有视频的up主
    if series["latest_video_id"] and (not df["latest_video_id"].isin([series["latest_video_id"]]).any()):
        return True
    if series["latest_stream_id"] and (not df["latest_stream_id"].isin([series["latest_stream_id"]]).any()):
        return True
    return False
