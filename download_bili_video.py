import pandas as pd
from Common.Abspath import *
from Common.Process import *
from Common.Logger import *
from DataAccess.DataBase import *
from DataAccess.sql_bilibili import *
from Web.biliAccess import *

if __name__ == "__main__":
    pm = ProcessManager()
    pm.StartWorkers(5)
    db = DataBase()
    db.Connect()

    csv_words = []
    with open(abspath("./.cache/bili_download_all.csv"), "r", encoding="utf-8") as f:
        csv_words = f.read().splitlines()
    csv_words = list(set(csv_words))

    upids = []
    updf = get_whole_table(db, "up")
    for i in range(len(updf)):
        upseries = updf.iloc[i]
        if upseries["up_name"] in csv_words or upseries["up_id"] in csv_words:
            upids.append(upseries["up_id"])

    root = abspath(r"./.download/")
    vids = []
    count = 0
    for upid in upids:
        videodf = get_allvideoinfo_byupid(db, upid)
        print(f"\r{float((count+1) / len(upids)) * 100:.2f}%", end="")
        count += 1
        for i in range(len(videodf)):
            vseries = videodf.iloc[i]
            if vseries["isCharge"] == 1:
                continue
            if vseries["duration"] > 3600:  # 短视频
                continue
            downfold = os.path.join(root, upid)
            downfold = os.path.join(downfold, vseries["v_id"])
            downfold = downfold + "\\"
            vids.append([vseries["v_id"], downfold, vseries["duration"]])
            # pm.AddTask(download_video, *[vseries["v_id"], downfold, default_bili_cookie_ytdlp, 1])
    print()
    random.shuffle(vids)
    print(len(vids))
    for v in vids:
        pm.AddTask(download_video, *[v[0], v[1], default_bili_cookie_ytdlp, 1])
        # download_video(v[0], v[1], default_bili_cookie_ytdlp, 1)
    pm.WaitAll()
    db.Disconnect()
