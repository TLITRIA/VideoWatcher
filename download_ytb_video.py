import pandas as pd
from Common.Abspath import *
from Common.Process import *
from Common.Logger import *
from DataAccess.DataBase import *
from DataAccess.sql_ytb import *
from Web.biliAccess import *

if __name__ == "__main__":
    pm = ProcessManager()
    pm.StartWorkers(5)
    db = DataBase()
    db.Connect()

    upids = get_all_up_id(db, "ytbup")
    csvids = []
    with open(abspath("./.cache/ytb_download_all.csv"), "r", encoding="utf-8") as f:
        csvids = f.read().splitlines()
    
    # 更新up相关信息
    
    # 下载视频

    tmplist = []
    for upid in upids:
        data = []
        data.append(f"https://www.youtube.com/@{upid}")
        df = ytb_get_oldestvideoinfo_byupid(db, upid)
        if df.empty or df.iloc[0]['upload'] == 0:
            continue
        series = df.iloc[0]
        data.append(series["url"])
        datatime = series["upload"]
        data.append(datatime)
        data.append(datetime.fromtimestamp(datatime).strftime("%Y-%m-%d"))
        tmplist.append(data)

    tmplist.sort(key=lambda x: x[2])
    for data in tmplist:
        print(data)
    print(len(tmplist))

    pm.WaitAll()
    db.Disconnect()
