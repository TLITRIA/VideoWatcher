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
    ytbtype INT, -- 类型：0 其他/默认 1 视频 2 直播 3 短视频
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


def ytb_up_is_unfilled(series: pd.Series) -> bool:
    return (
        series["up_name"] is None
        or series["intro"] is None
        # or series["face"] is None
        or series["data_time"] is None
        or series["latest_video_id"] is None
        or series["latest_stream_id"] is None
        or series["latest_short_id"] is None
        or series["up_sum"] is None
        or series["last_update_video_time"] is None
    )


def ytb_get_allvideoinfo_byupid(db: DataBase, up_id: str) -> pd.DataFrame:
    return get_allvideoinfo_byupid(db, up_id, "ytbvideo")


def ytb_get_oldestvideoinfo_byupid(db: DataBase, up_id: str) -> pd.DataFrame:
    if not db.isConnected or up_id == "":
        return pd.DataFrame()
    sql = f"SELECT * FROM ytbvideo WHERE up_id IS '{up_id}' ORDER BY upload;"
    df = pd.read_sql_query(sql, db.conn)
    return df


class YtbEnum(Enum):
    """
    < 0 有问题但不需要更新
    = 0 没问题也不需要更新
    > 0 需要更新
    """

    DoNothing = -1  # 有问题但不需要更新
    NoNeedToUpdate = 0  # 不需要更新

    UpNeedDeleteALL = 1  # 需要删除up的所有视频并更新
    UpMissInfo = 2  # up信息缺失
    UpLongTimeNoUpdate = 3  # up长时间未更新
    UpVideoSumTooSmall = 4  # up的视频数太少
    UpLastVidNotInDB = 5  # up的最新不在数据库中
    UpLastVideoNotInDB = 6  # up的最新视频不在数据库中
    UpLastShortNotInDB = 7  # up的最新短视频不在数据库中
    UpLastStreamNotInDB = 8  # up的最新直播回放不在数据库中


def judge_ytbUp_needupdate(db: DataBase, up_id: str) -> tuple[str, Enum]:
    updf = ytb_get_up_info(db, up_id)
    if len(updf) != 1:
        return f"{up_id} doesn't exist in database", YtbEnum.DoNothing
    series = updf.iloc[0]
    if ytb_up_is_unfilled(series):
        return f"{up_id} miss info", YtbEnum.UpMissInfo
    timeout = 60 * 60 * 24 * 7
    timeout_string = generate_duration_string(timeout)
    if not series["data_time"] or int(series["data_time"]) < get_timestamp() - timeout:  # up信息未更新
        return f"{up_id} didn't update for at least {timeout_string}", YtbEnum.UpLongTimeNoUpdate
    if (
        not series["last_update_video_time"] or int(series["last_update_video_time"]) < get_timestamp() - timeout
    ):  # up视频信息未更新
        return f"{up_id}'s video didn't update for at least {timeout_string}", YtbEnum.UpLongTimeNoUpdate
    videodf = ytb_get_allvideoinfo_byupid(db, up_id)
    if videodf.empty:
        return f"{up_id} has no video", YtbEnum.UpVideoSumTooSmall
    if series["latest_video_id"] and (not videodf["v_id"].isin([series["latest_video_id"]]).any()):
        return f"{up_id} last video not in database", YtbEnum.UpLastVideoNotInDB
    if series["latest_stream_id"] and (not videodf["v_id"].isin([series["latest_stream_id"]]).any()):
        return f"{up_id} last stream not in database", YtbEnum.UpLastStreamNotInDB
    if series["latest_short_id"] and (not videodf["v_id"].isin([series["latest_short_id"]]).any()):
        return f"{up_id} last short not in database", YtbEnum.UpLastShortNotInDB
    offset = 10
    sumExist = len(videodf)
    if series["up_sum"]:
        if int(series["up_sum"]) - sumExist > offset:  # 视频数量少于up_sum
            return f"{up_id} sumExist is at least {offset} less than up_sum", YtbEnum.UpVideoSumTooSmall
        # elif int(series["up_sum"]) < sumExist:
        #     return f"{up_id} need delete all video then update", YtbEnum.UpNeedDeleteALL
    return "", YtbEnum.NoNeedToUpdate
