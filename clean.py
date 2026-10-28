"""项目清理"""

# 暂时收集可能的选项，目前没有一定要做的必要

"""
数据库
多余的数据
    up_exclude yes_no为0的数据
多余的表格
    程序异常退出会留下名为"_{时间戳}"的临时表格
核对每一列数据是否正常解析
自动备份 done

文件清理

格式化
*.py文件全部用black格式化 done

隐私数据
不能硬编码用于测试功能的
B站
    视频id
    up主id
    用户名
window系统用户名
cookie数值
"""
import os, sys
import subprocess

from Common.Abspath import *
from DataAccess.DataBase import *
from DataAccess.sql_bilibili import *
from DataAccess.sql_ytb import *


def task_clean_database():
    db = DataBase()
    l = Logger()

    db.Connect()

    # l.info("检查数据是否符合规范")

    l.info("删除up_exclude表中yes_no为0的记录")
    sql = "DELETE FROM up_exclude WHERE yes_no = 0;"
    db.ExecuteNow(sql)

    l.info("BiliBili统计需要更新的数据")
    df = get_whole_table(db, "up")
    df = df.sort_values(by="data_time")
    results: dict = {}
    for i in range(len(df)):
        ret, enum = judge_bilibiliUP_needupdate(db, str(df.loc[i, "up_id"]))
        results[enum.name] = results.get(enum.name, 0) + 1
        if enum.value > 0:
            print(enum.name, "\t", ret)
    l.info(f"BiliBili数据统计：{str(results)}")

    l.info("Ytb统计需要更新的数据")
    df = get_whole_table(db, "ytbup")
    df = df.sort_values(by="data_time")
    results: dict = {}
    for i in range(len(df)):
        up_id = str(df.loc[i, "up_id"])
        ret, enum = judge_ytbUp_needupdate(db, up_id)
        results[enum.name] = results.get(enum.name, 0) + 1
        if enum.value > 0:
            print(enum.name, "\t", ret)
    l.info(f"Ytb数据统计：{str(results)}")

    db.Disconnect()


def task_clean_project_file(): ...


def task_black_format_py_file():
    """格式化所有py文件"""
    l = Logger()
    l.info("Black格式化所有用户创建的xxx.py文件")
    project_root = abspath(R"./")
    dir_blacklists = [
        abspath(R"./.venv/"),
        abspath(R"./.cache/"),
        abspath(R"./.download/"),
        abspath(R"./UI/"),
    ]
    name_blacklists = ["__pycache__", ".git", ".idea"]
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if root in dir_blacklists or any(name in root for name in dir_blacklists + name_blacklists):
                    continue
                l.info(f"Black format file: {file_path}")
                result = subprocess.run(
                    ["black", file_path, "-l", "120"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )


task_clean_database()
task_black_format_py_file()
