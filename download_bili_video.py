import pandas as pd
from Common.Abspath import *
from Common.Process import *
from Common.Logger import *
from DataAccess.DataBase import *
from DataAccess.sql_bilibili import *
from Web.biliAccess import *

if __name__ == "__main__":
    pm = ProcessManager()
    pm.StartWorkers(2)
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

    datalist = []
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
            downfold = os.path.join(download_root, upid)
            downfold = os.path.join(downfold, vseries["v_id"])
            downfold = downfold + "\\"
            datalist.append([vseries["v_id"], downfold, vseries["duration"]])
            # pm.AddTask(download_video, *[vseries["v_id"], downfold, default_bili_cookie_ytdlp, 1])
    print()
    random.shuffle(datalist)
    print('视频总数', len(datalist))

    dsum_yes = 0
    dsum_no = 0
    dsum_size_yes = 0
    dsum_size_no = 0
    for i, (v_id, downfold, duration) in enumerate(datalist):
        print(f"\r{float((i+1) / len(datalist)) * 100:.2f}%", end="")
        if os.path.exists(downfold) and scan_foldsize(downfold) > 0:
            dsum_yes += duration
            dsum_size_yes += scan_foldsize(downfold)
        else:
            dsum_no += duration
    print()
    dsum_size_no = int(dsum_size_yes * dsum_no / dsum_yes) if dsum_yes > 0 else 0
    val1 = int(dsum_size_yes / dsum_yes) if dsum_yes > 0 else 0
    print("根据已有的数据估算磁盘占用/时长s=", generate_size_string(val1))
    print("已下载时长", generate_duration_string(dsum_yes))
    print("未下载时长", generate_duration_string(dsum_no))
    print("已下载大小", generate_size_string(dsum_size_yes))
    print("未下载大小", generate_size_string(dsum_size_no))


    size_count = 0
    num_count = 0
    for v in datalist:
        if os.path.exists(v[1]) and scan_foldsize(v[1]) > 0:
            continue
        size_count += val1 * v[2]
        num_count += 1
        if size_count > 1024 ** 3: # 限制下载数量
            break
        pm.AddTask(download_video, *[v[0], v[1], default_bili_cookie_ytdlp, 1])
    # download_video(v[0], v[1], default_bili_cookie_ytdlp, 1)
    print('已添加任务数', num_count)
    pm.WaitAll()
    db.Disconnect()
