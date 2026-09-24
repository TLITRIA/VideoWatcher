from DataAccess.DataBase import *
from os.path import abspath
import traceback
from Common.Logger import *
from PyQt6.QtCore import Qt

"""
数据库操作语句
设想中B站和油管都要求有同样的数据
"""
videowatcher_sql_fp = abspath(R"./.cache/db/videowatcher.db")
videowatcher_sqls = [
    """
CREATE TABLE IF NOT EXISTS up(
    up_id TEXT,
    up_name TEXT, -- up主名字
    intro TEXT, -- up主页简介
    face TEXT, -- up主头像链接
    up_sum INT, -- up视频总数
    up_last_vid TEXT, -- 最近更新视频id
    up_last_time TEXT, -- 最近更新视频时间
    data_time INT, -- 数据更新时间
    tag_time INT, -- tag更新时间
    PRIMARY KEY (up_id)
);""",  # TODO url
    """
CREATE TABLE IF NOT EXISTS up_tag(
    up_id TEXT NOT NULL, -- up主id号
    tag TEXT NOT NULL, -- tag标签
    PRIMARY KEY (up_id, tag)
);""",
    """
CREATE TABLE IF NOT EXISTS video(
    v_id TEXT , -- 视频id号
    up_id TEXT, -- up主id号
    title TEXT, -- 视频标题
    cover TEXT, -- 视频封面链接
    upload TEXT, -- 视频上传时间
    play INT, -- 播放量
    danmu INT, -- 弹幕数
    duration INT, -- 视频时长
    isCharge INT, -- 视频是否付费
    data_time INT, -- 数据更新时间
    tag_time INT, -- tag更新时间
    PRIMARY KEY (v_id)
);""",  # TODO url
    """
CREATE TABLE IF NOT EXISTS video_tag(
    v_id TEXT NOT NULL, -- 视频id号
    tag TEXT NOT NULL, -- tag标签
    PRIMARY KEY (v_id, tag)
);""",
    """
CREATE TABLE IF NOT EXISTS up_exclude(
    up_id TEXT NOT NULL, -- up主id号
    reason TEXT, -- 排除原因
    yes_no INT, -- 是否排除 1是 0否
    PRIMARY KEY (up_id)
);""",  # TODO url
]


# ============================================================ #
def create_all(db: DataBase, sqls: list):
    """创建所有表"""
    for sql in sqls:
        try:
            db.ExecuteNow(sql)
        except:
            print("-" * 80)
            print(sql)
            traceback.print_exc()


def insert_up_null(db: DataBase, up_id: str, table="up"):
    """向up表中插入除up_id外其他字段为null的数据"""
    if not db.isConnected:
        return False
    sql = f"INSERT INTO {table}(up_id) VALUES('{up_id}');"
    try:
        db.ExecuteNow(sql)
        return True
    except:
        return False


def insert_up(db: DataBase, df: pd.DataFrame, table="up"):
    """向up表中插入数据，会自动选择插入哪些字段，不插入哪些字段"""
    if not db.isConnected:
        return False
    result = db.conn.execute(f"PRAGMA table_info({table})")
    db_columns = [row[1] for row in result]
    columns_to_write = [col for col in df.columns if col in db_columns]
    df_filtered = df[columns_to_write]
    temp_table = "_" + str(get_timestamp())
    df_filtered.to_sql(temp_table, db.conn, if_exists="replace", index=False)

    columns = ", ".join(df_filtered.columns)
    select_sql = ", ".join(
        [
            f"{tag} = (SELECT {tag} FROM {temp_table} WHERE {table}.up_id = {temp_table}.up_id)"
            for tag in df_filtered.columns
        ]
    )
    sql = f"""
    UPDATE {table}
    SET {select_sql}
    WHERE EXISTS (SELECT 1 FROM {temp_table} WHERE {table}.up_id = {temp_table}.up_id);
    """
    db.conn.execute(sql)
    sql = f"""
    INSERT INTO {table} ({columns})
    SELECT {columns}
    FROM {temp_table}
    WHERE up_id NOT IN (SELECT up_id FROM {table});
    """
    db.conn.execute(sql)
    db.conn.execute(f"DROP TABLE {temp_table}")
    db.conn.commit()
    return True


def insert_video(db: DataBase, df: pd.DataFrame, table="video"):
    """向video表中插入数据，会自动选择插入哪些字段，不插入哪些字段"""
    if not db.isConnected:
        return False
    result = db.conn.execute(f"PRAGMA table_info({table})")
    db_columns = [row[1] for row in result]
    columns_to_write = [col for col in df.columns if col in db_columns]
    df_filtered = df[columns_to_write]
    temp_table = "_" + str(get_timestamp())
    df_filtered.to_sql(temp_table, db.conn, if_exists="replace", index=False)

    columns = ", ".join(df_filtered.columns)
    select_sql = ", ".join(
        [
            f"{tag} = (SELECT {tag} FROM {temp_table} WHERE {table}.v_id = {temp_table}.v_id)"
            for tag in df_filtered.columns
        ]
    )
    sql = f"""
    UPDATE {table}
    SET {select_sql}
    WHERE EXISTS (SELECT 1 FROM {temp_table} WHERE {table}.v_id = {temp_table}.v_id);
    """
    db.conn.execute(sql)
    sql = f"""
    INSERT INTO {table} ({columns})
    SELECT {columns}
    FROM {temp_table}
    WHERE v_id NOT IN (SELECT v_id FROM {table});
    """
    db.conn.execute(sql)
    db.conn.execute(f"DROP TABLE {temp_table}")
    db.conn.commit()
    return True


def insert_up_tag(db: DataBase, up_id: str, tag: str, table="up_tag"):
    """插入up_tag表"""
    if not db.isConnected or not up_id or not tag:
        return False
    sql = f"INSERT INTO {table}(up_id, tag) VALUES ('{up_id}', '{tag}');"
    db.ExecuteNow(sql)
    update_up_tagtime(db, up_id)
    return True


def insert_video_tag(db: DataBase, video_id: str, tag: str):
    """插入video_tag表"""
    if not db.isConnected or not video_id or not tag:
        return False
    sql = f"INSERT INTO video_tag(v_id, tag) VALUES ('{video_id}', '{tag}');"
    db.ExecuteNow(sql)
    return True


# ============================================================ #
def delete_up(db: DataBase, up_id: str):
    """从up表删除记录"""
    if not db.isConnected or not up_id:
        return False
    sql = f"DELETE FROM up WHERE up_id='{up_id}';"
    db.ExecuteNow(sql)
    return True


def delete_up_tag(db: DataBase, up_id: str, tag: str, table="up_tag"):
    """删除up_tag表"""
    if not db.isConnected or not up_id or not tag:
        return False
    sql = f"DELETE FROM {table} WHERE up_id='{up_id}' AND tag='{tag}';"
    db.ExecuteNow(sql)
    update_up_tagtime(db, up_id)
    return True


def delete_video_tag(db: DataBase, video_id: str, tag: str):
    """删除video_tag表"""
    if not db.isConnected or video_id == "" or tag == "":
        return False
    sql = f"DELETE FROM video_tag WHERE v_id='{video_id}' AND tag='{tag}';"
    db.ExecuteNow(sql)
    return True


def delete_allvideo_byupid(db: DataBase, up_id: str, table: str = "video"):
    """通过给出的up_id删除视频表中对应的视频"""
    if not db.isConnected or up_id == "" or table == "":
        return False
    sql = f"DELETE FROM {table} WHERE up_id = '{up_id}';"
    db.ExecuteNow(sql)
    return True

# ============================================================ #
def update_one_up_exclude(db: DataBase, up_id: str, reason: str, yes_no: bool):
    """更新up_exclude表，会自动创建记录"""
    if not db.isConnected or not up_id:
        return False
    val = 1 if yes_no else 0
    sql = f"SELECT * FROM up_exclude WHERE up_id='{up_id}';"  # check if up_id exists
    if db.conn.execute(sql).fetchone() is not None:
        sql = f"UPDATE up_exclude SET reason='{reason}', yes_no={val} WHERE up_id='{up_id}';"
        db.ExecuteNow(sql)
    else:
        sql = f"INSERT INTO up_exclude(up_id, reason, yes_no) VALUES ('{up_id}', '{reason}', {val});"
        db.ExecuteNow(sql)
    return True


def update_up_tagtime(db: DataBase, up_id: str, table="up"):
    """更新up表tag的更新时间"""
    if not db.isConnected or up_id == "":
        return False
    if exist_up(db, up_id):
        sql = f"UPDATE {table} SET tag_time={str(get_timestamp())} WHERE up_id='{up_id}';"
        db.ExecuteNow(sql)


# ============================================================ #
def exist_up(db: DataBase, up_id: str) -> bool:
    """判断up主是否存在于up表中"""
    sql = f"SELECT * FROM up WHERE up_id='{up_id}';"
    if db.isConnected and up_id:
        return db.conn.execute(sql).fetchone() is not None
    else:
        return False


def exist_up_exclude(db: DataBase, up_id: str):
    """判断up主是否存在于up排除表中"""
    sql = f"SELECT yes_no FROM up_exclude WHERE up_id='{up_id}';"
    if db.isConnected and up_id:
        if db.conn.execute(sql).fetchone() is not None:
            return db.conn.execute(sql).fetchone()[0] == 1
        else:
            return False
    else:
        return False


def get_up_collection_state(db: DataBase, up_id: str) -> Qt.CheckState:
    """获取up主收藏状态，注意返回值对应的含义"""
    val1 = exist_up(db, up_id)
    val2 = exist_up_exclude(db, up_id)
    if not val1 and not val2:
        return Qt.CheckState.Unchecked
    elif val1:
        return Qt.CheckState.PartiallyChecked
    elif val2:
        return Qt.CheckState.Checked
    else:
        return Qt.CheckState.Unchecked


def get_all_up_exclude_df(db: DataBase) -> pd.DataFrame:
    """获取所有up_exclude中的信息"""
    df = pd.DataFrame()
    if not db.isConnected:
        return df
    sql = f"SELECT * FROM up_exclude;"
    df = pd.read_sql_query(sql, db.conn)
    return df


def get_up_info(db: DataBase, up_id: str, table="up") -> pd.DataFrame:
    """从up表中获取up主信息"""
    df = pd.DataFrame()
    if not db.isConnected or not up_id:
        return df
    sql = f"SELECT * FROM {table} WHERE up_id='{up_id}';"
    df = pd.read_sql_query(sql, db.conn)
    return df


def get_video_info(db: DataBase, v_id: str, table="video") -> pd.DataFrame:
    """从video表中获取视频信息"""
    df = pd.DataFrame()
    if not db.isConnected or not v_id:
        return df
    sql = f"SELECT * FROM {table} WHERE v_id='{v_id}';"
    df = pd.read_sql_query(sql, db.conn)
    return df


def get_up_selectedtags(db: DataBase, up_id: str, table="up_tag") -> list:
    """获取up_tag表中up选中的tag"""
    ret = []
    if not db.isConnected or up_id == "":
        return ret
    sql = f"SELECT tag FROM {table} WHERE up_id='{up_id}';"
    ret = [row[0] for row in db.conn.execute(sql).fetchall()]
    ret = sorted(list(set(ret)))
    return ret


def get_up_unselectedtags(db: DataBase, up_id: str, table="up_tag") -> list:
    """获取up_tag表中up未选中的tag"""
    ret = []
    if not db.isConnected or up_id == "":
        return []
    sql = f"SELECT tag FROM {table} WHERE tag NOT IN (SELECT tag FROM {table} WHERE up_id='{up_id}');"
    ret = [row[0] for row in db.conn.execute(sql).fetchall()]
    ret = sorted(list(set(ret)))
    return ret


def get_video_selectedtags(db: DataBase, v_id: str) -> list:
    """获取video_tag表中video选中的tag"""
    ret = []
    if not db.isConnected or v_id == "":
        return ret
    sql = f"SELECT tag FROM video_tag WHERE v_id='{v_id}';"
    ret = [row[0] for row in db.conn.execute(sql).fetchall()]
    ret = sorted(list(set(ret)))
    return ret


def get_video_unselectedtags(db: DataBase, v_id: str) -> list:
    """获取video_tag表中video未选中的tag"""
    ret = []
    if not db.isConnected or v_id == "":
        return []
    sql = f"SELECT tag FROM video_tag WHERE tag NOT IN (SELECT tag FROM video_tag WHERE v_id='{v_id}');"
    ret = [row[0] for row in db.conn.execute(sql).fetchall()]
    ret = sorted(list(set(ret)))
    return ret


def get_up_unfilled(db: DataBase) -> list:
    """获取up表中数据残缺的up_id"""
    ret = []
    if not db.isConnected:
        return []
    # 定义什么样的数据是残缺的
    sql = "SELECT up_id FROM up WHERE up_name IS NULL OR face IS NULL OR up_last_time IS NULL;"
    ret = [row[0] for row in db.conn.execute(sql).fetchall() if row[0] != ""]
    ret = sorted(list(set(ret)))
    return ret


def get_all_up_id(db: DataBase) -> list:
    """获取up表中所有up_id"""
    ret = []
    if not db.isConnected:
        return []
    sql = "SELECT up_id FROM up ORDER BY data_time;"  # 按照更新时间从前往后
    ret = [row[0] for row in db.conn.execute(sql).fetchall() if row[0] != ""]
    return ret


def get_all_up_info(db: DataBase) -> pd.DataFrame:
    df = pd.DataFrame()
    if not db.isConnected:
        return df
    for up_id in get_all_up_id(db):
        df = pd.concat([df, get_up_info(db, up_id)], ignore_index=True)
    return df


def get_upexclude_up_fullinfo(db: DataBase) -> pd.DataFrame:
    """搜索所有排除的up并从up表中查询信息"""
    df = pd.DataFrame()
    if not db.isConnected:
        return df

    sql = "SELECT up_id FROM up_exclude WHERE yes_no = 1;"
    up_ids = [row[0] for row in db.conn.execute(sql).fetchall() if row[0] != ""]
    up_ids = sorted(list(set(up_ids)))

    for up_id in up_ids:
        df = pd.concat([df, get_up_info(db, up_id)], ignore_index=True)
    return df


def get_all_taged_video_df(db: DataBase) -> pd.DataFrame:
    """搜索所有拥有tag的video"""
    df = pd.DataFrame()
    if not db.isConnected:
        return df

    sql = "SELECT v_id FROM video_tag;"
    v_ids = [row[0] for row in db.conn.execute(sql).fetchall() if row[0] != ""]
    v_ids = sorted(list(set(v_ids)))

    for v_id in v_ids:
        df = pd.concat([df, get_video_info(db, v_id)], ignore_index=True)
    return df


def get_up_id_whichvideoisnotnew(db: DataBase) -> list:
    """获取up表中缺少最新video的up_id"""
    ret = []
    if not db.isConnected:
        return []
    sql = """
    SELECT up_id FROM up 
    WHERE up_last_vid IS NOT NULL 
        AND up_last_vid NOT IN 
        (SELECT v_id FROM video 
        WHERE video.up_id=up.up_id);"""
    ret = [row[0] for row in db.conn.execute(sql).fetchall() if row[0] != ""]
    ret = sorted(list(set(ret)))
    return ret


def get_len_missingvideo(db: DataBase, up_id: str) -> int:
    """获取up缺少的video数量"""
    ret = 0
    if not db.isConnected or up_id == "":
        return 0
    try:
        sql = f"""
        SELECT COUNT(*) FROM video
        WHERE video.up_id={up_id};
        """
        video_existed = int(db.conn.execute(sql).fetchone()[0])
        sql = f"""
        SELECT up_sum FROM up
        WHERE up.up_id={up_id}
        AND up_sum IS NOT NULL;
        """
        video_sum = int(db.conn.execute(sql).fetchone()[0])
        ret = video_sum - video_existed
    except:
        ret = 0
    return ret


def search_up_bytags(db: DataBase, tags: list) -> list:
    up_ids = []
    if not db.isConnected:
        return []
    for tag in tags:
        sql = f"SELECT up_id FROM up_tag WHERE tag IS '{tag}';"
        tmp_ids = [
            row[0] for row in db.conn.execute(sql).fetchall() if row[0] != ""
        ]
        up_ids.extend(tmp_ids)
    return list(set(up_ids))


def get_allvideoinfo_byupid(
    db: DataBase, up_id: str, table="video"
) -> pd.DataFrame:
    df = pd.DataFrame()
    if not db.isConnected:
        return df
    sql = f"SELECT * FROM {table} WHERE up_id IS '{up_id}';"
    df = pd.read_sql_query(sql, db.conn)
    return df
