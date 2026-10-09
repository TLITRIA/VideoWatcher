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
    up_sum INT, -- up主上传视频数
    latest_video_id TEXT, -- 最新视频id
    latest_stream_id TEXT, -- 最新直播id
    latest_short_id TEXT, -- 最新短视频id
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
    # 不搞排除表
    # 油管shorts视频链接与videos streams链接的格式不同
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
        "OR latest_video_id IS NULL "
        "OR latest_stream_id IS NULL "
        "OR latest_short_id IS NULL "
        "OR up_sum IS NULL "
        "OR last_update_video_time IS NULL;"
    )
    ret = [row[0] for row in db.conn.execute(sql).fetchall() if row[0] != ""]
    ret = sorted(list(set(ret)))
    return ret


def ytb_get_allvideoinfo_byupid(db: DataBase, up_id: str) -> pd.DataFrame:
    return get_allvideoinfo_byupid(db, up_id, "ytbvideo")


def ytb_get_oldestvideoinfo_byupid(db: DataBase, up_id: str) -> pd.DataFrame:
    if not db.isConnected or up_id == "":
        return pd.DataFrame()
    sql = f"SELECT * FROM ytbvideo WHERE up_id IS '{up_id}' ORDER BY upload;"
    df = pd.read_sql_query(sql, db.conn)
    return df


def judge_ytbUp_needupdate(db: DataBase, up_id: str) -> bool:
    updf = ytb_get_up_info(db, up_id)
    if len(updf) != 1:
        return False  # 查无此人不处理
    series = updf.iloc[0]
    if series["up_id"] in ytb_get_up_unfilled(db):
        return True
    if not series["data_time"] or int(series["data_time"]) < get_timestamp() - 60 * 60 * 24 * 7:  # up信息未更新
        return True
    if (
        not series["last_update_video_time"]
        or int(series["last_update_video_time"]) < get_timestamp() - 60 * 60 * 24 * 7
    ):  # up视频信息未更新
        return True
    videodf = ytb_get_allvideoinfo_byupid(db, up_id)
    if videodf.empty:
        return True
    if series["latest_video_id"] and (not videodf["v_id"].isin([series["latest_video_id"]]).any()):
        return True  # 最新视频id不在ytbvideo表中
    if series["latest_stream_id"] and (not videodf["v_id"].isin([series["latest_stream_id"]]).any()):
        return True  # 最新直播id不在ytbvideo表中
    if series["latest_short_id"] and (not videodf["v_id"].isin([series["latest_short_id"]]).any()):
        return True  # 最新短片id不在ytbvideo表中
    if series["up_sum"] and int(series["up_sum"]) - len(videodf) > 10:  # 视频数量少于up_sum
        return True
    return False
