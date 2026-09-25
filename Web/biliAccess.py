from Web.MyWebDriver import *
import time
import shutil

import pandas as pd
from Common.Abspath import default_bili_cookietxt
from Common.Process import *
from Common.Common import scan_foldsize
from DataAccess.DataBase import *
from DataAccess.sql_query import *


def sum_duration(df: pd.DataFrame) -> int:
    ret = 0
    for i in range(len(df)):
        series = df.iloc[i]
        if "duration" in series.index.tolist():
            ret += int(series["duration"])
    return ret


def remove_video_fromFold(datalist) -> bool:
    wd = MyWebDriver()
    wd.selenium_options.append("--force-dark-mode")
    wd.selenium_options.append("--mute-audio")
    wd.Login()
    wd._driver.minimize_window()

    for index, [video_id, fold_id] in enumerate(datalist):
        print(f"正在处理第{index+1}个视频")

        if not video_id or not fold_id:
            continue
        url = f"https://www.bilibili.com/video/{video_id}/"
        if not wd._driver.current_url.startswith(url):
            wd.Goto(url)
            time.sleep(3)

        nodes = wd.xpath_wait("//div[@title='收藏（E）']")
        if nodes:
            wd.ClickNode(nodes[0])
            time.sleep(1)
        else:
            continue
        nodes = wd.xpath_wait('//div/ul/li/label[./input[@type="checkbox"]]')
        if nodes:
            for node in nodes:
                _nodes = xpath(node, './input[@type="checkbox"]')
                if _nodes and _nodes[0].is_selected() and fold_id in node.text:
                    wd.ClickNode(_nodes[0])
                    time.sleep(0.5)
            but_comfirm = wd.xpath_findall("//button[contains(text(), '确定')]")[0]
            wd.ClickNode(but_comfirm)
            time.sleep(1)
    wd.Quit()
    return True


def goto_default_collectfolder(wd: MyWebDriver):
    if not wd.ifLoginBilibili():
        wd.Login()

    wd.Goto("https://space.bilibili.com/")
    nodes = wd.xpath_wait("//a[@class='nav-tab__item']")
    if nodes:
        wd.ClickNode(nodes[3])
        time.sleep(1)

    # TODO 自动点击按钮：清除失效内容
    return True


def goto_TODOWN_collectfolder(wd: MyWebDriver):
    if not wd.ifLoginBilibili():
        wd.Login()
    wd.Goto("https://www.bilibili.com/")
    wd.ClickGotoNode(wd.xpath_wait("//span[contains(text(), '收藏')]")[0])
    wd.xpath_wait('//div[@class="bili-video-card__wrap"]')


def download_video(bv, downfold, cookie="", limit_rate: int = 0, possible_title: str = "") -> subprocess.CompletedProcess:
    """下载B站视频"""
    url = BV2url(bv)
    if os.path.exists(downfold):
        if scan_foldsize(downfold) > 0:
            print(f"文件夹 {downfold} 已存在且不为空，跳过下载")
            return subprocess.CompletedProcess(args=[], returncode=0)
    else:
        g_mkdir_byfp(downfold)

    cmd = ["yt-dlp"]
    cmd.extend(["--no-check-certificate"] if cookie == "" else ["--cookies", cookie])  # 使用cookie
    if limit_rate > 0:
        cmd.extend(["-r", f"{limit_rate}m"])  # 限速
    # TODO 画质选择
    cmd.append("-i")
    cmd.extend(["-o", f"{downfold}%(title)s.%(ext)s"])  # 输出格式
    # 字幕文件
    cmd.extend(["--write-subs", "--write-auto-subs"])
    cmd.extend(["--sub-langs", "en,zh-Hans,ai-zh,ai-en"])
    cmd.extend(["--convert-subs", "srt"])
    cmd.extend(["-o", f"subtitle:{downfold}%(title)s.%(ext)s"])

    cmd.append(url)
    print(cmd)
    result = subprocess.run(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr, text=True)
    time.sleep(5)
    return result


if __name__ == "__main__":
    download_video("BV1scoDYeEFi", abspath(R"./.cache/downloadtest/") + "/", default_bili_cookie_ytdlp)

    """下载downloadAll up主的视频每人下载最新的一个，若已存在则选择前一个以此类推"""
    # pm = ProcessManager()
    # pm.StartWorkers(3)
    # db = DataBase()
    # db.Connect(test_db_fp)

    # up_tags = ["downloadAll"]
    # upids = search_up_bytags(db, up_tags)
    # df = pd.DataFrame()
    # for upid in upids:
    #     df = pd.concat([df, get_allvideoinfo_byupid(db, upid)], ignore_index=True)

    # root = abspath(r"./.cache/download_specified_tags/")

    # for upid in upids:
    #     tmpdf = df[df["up_id"] == upid]
    #     for i in range(len(tmpdf)):
    #         series = tmpdf.iloc[i]
    #         downfold = os.path.join(root, upid)
    #         downfold = os.path.join(downfold, series["v_id"])
    #         downfold = downfold + "\\"
    #         if os.path.exists(downfold):
    #             continue
    #         print(downfold, end="\n")
    #         # download_video(series['v_id'], downfold)
    #         pm.AddTask(download_video, *[series["v_id"], downfold])
    #         break

    # pm.__del__()
    # db.Disconnect()
