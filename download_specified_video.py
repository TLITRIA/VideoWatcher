"""下载指定tag和条件的视频"""

import pandas as pd
from Common.Abspath import default_bili_cookietxt
from Common.Process import *
from DataAccess.DataBase import *
from DataAccess.sql_query import *
from Web.biliAccess import *

if __name__ == "__main__":
    pm = ProcessManager()
    pm.StartWorkers(1)
    db = DataBase()
    db.Connect("D:/__Downloads__/videowatcher.db")

    # 获取拥有tag的up的所有视频
    up_tags = ["downloadAll"]
    upids = search_up_bytags(db, up_tags)
    df = pd.DataFrame()
    for upid in upids:
        df = pd.concat([df, get_allvideo_byupid(db, upid)], ignore_index=True)

    # 筛选视频

    # 下载视频
    root = abspath(r"./.cache/download_specified_tags/")
    count = 0
    for upid in upids:
        tmpdf = df[df["up_id"] == upid]
        for i in range(len(tmpdf)):
            if i > 1: 
                break
            series = tmpdf.iloc[i]
            if int(series["duration"]) > 60:
                continue
            downfold = os.path.join(root, upid)
            downfold = os.path.join(downfold, series["v_id"])
            downfold = downfold + "\\"
            if os.path.exists(downfold):
                continue
            print(downfold, end="\n")
            # pm.AddTask(download_video, *[series["v_id"], downfold, default_bili_cookie_ytdlp, 1])
            download_video(series["v_id"], downfold, default_bili_cookie_ytdlp, 1)
            count += 1
    print(count)
    # pm.WaitAll()
    db.Disconnect()
