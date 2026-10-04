import re
import pandas as pd
import traceback
from Web.MyWebDriver import *
from Common.Logger import *
from Common.match_ytb import *
from DataAccess.sql_ytb import *
from Web.ytbAccess import *


def parse_ytb_latestvid(wd: MyWebDriver) -> str:
    latest_video_id = ""
    nodes = wd.xpath_wait(f"//ytd-rich-item-renderer")
    if len(nodes) != 0:
        _nodes = xpath(nodes[0], "./div/yt-lockup-view-model/div/a[@class='ytLockupViewModelContentImage']")
        if len(_nodes):
            latest_video_id = match_ytb_vid_byUrl(str(_nodes[0].get_attribute("href")))
    return latest_video_id


def parse_YtbUp(wd: MyWebDriver, db: DataBase, other: list = []):
    """
    由于油管up主部分没有videos界面或者部分没有streams界面
    以此为进入点，通过在other添加参数决定解析项
    目前只会解析videos和streams界面
    """
    if wd._isQuit or not hasattr(wd, "_driver"):
        return
    if not db.isConnected:
        return
    l = Logger()
    df = pd.DataFrame()
    info = []
    cols = []
    up_id = match_ytb_upid(wd._driver.current_url)
    if up_id == "":
        return
    info.append(up_id)
    cols.append("up_id")
    url = unquote(f"https://www.youtube.com/@{up_id}")
    info.append(url)
    cols.append("url")
    hasVideos = bool(len(wd.xpath_wait(f"//yt-tab-shape[@tab-title='视频']")))
    hasStreams = len(wd.xpath_wait(f"//yt-tab-shape[@tab-title='直播']"))
    try:
        nodes = wd.xpath_wait("//yt-dynamic-text-view-model")
        if len(nodes):
            up_name = nodes[0].text.strip()
            info.append(up_name)
            cols.append("up_name")
        nodes = wd.xpath_findall(
            "//truncated-text-content/span[@class='ytAttributedStringHost ytAttributedStringWhiteSpacePreWrap']"
        )
        if len(nodes):
            intro = nodes[0].text
            if intro == "详细了解此频道 ":
                intro = ""
            info.append(intro)
            cols.append("intro")
        nodes = wd.xpath_wait("//div[@class='ytSpecAvatarShapeAvatarSizeGiant']/img[@class and @src]")
        if len(nodes):
            face = nodes[0].get_attribute("src")
            info.append(face)
            cols.append("face")

        data_time = get_timestamp()
        info.append(data_time)
        cols.append("data_time")
    except:
        traceback.print_exc()
        l.error(traceback.format_exc())
    df = pd.DataFrame(data=[info], columns=cols)
    ytb_insert_up(db, df)
    # ======================================= #
    updf = ytb_get_up_info(db, up_id)
    if len(updf) != 0:
        if hasVideos:  # videos
            wd.Goto(f"https://www.youtube.com/@{up_id}/videos")
            time.sleep(10)
            nodes = wd.xpath_wait(f"//ytd-rich-item-renderer")
            updf.loc[0, "latest_video_id"] = parse_ytb_latestvid(wd)
            if "视频" in other:
                df = parse_YtbVideos(wd)
                if len(df) != 0:
                    ytb_insert_video(db, df)
                    l.info(f"{up_id} 已读取视频共 {len(df)} 条")

        if hasStreams:  # streams
            wd.Goto(f"https://www.youtube.com/@{up_id}/streams")
            time.sleep(10)
            nodes = wd.xpath_wait(f"//ytd-rich-item-renderer")
            updf.loc[0, "latest_stream_id"] = parse_ytb_latestvid(wd)
            if "直播" in other and hasStreams:
                df = parse_YtbVideos(wd, 2)
                if len(df) != 0:
                    ytb_insert_video(db, df)
                    l.info(f"{up_id} 已读取直播共 {len(df)} 条")

        updf.loc[0, "last_update_video_time"] = get_timestamp()
    ytb_insert_up(db, updf)


def parse_YtbVideos(wd: MyWebDriver, ytbtype: int = 1) -> pd.DataFrame:
    """
    解析油管videos页面列表    没有分页所以相较于解析bilibili视频页用时较长
    """
    df = pd.DataFrame()
    if wd._isQuit or not hasattr(wd, "_driver"):
        return df
    if not match_ytb_videos(wd._driver.current_url) and not match_ytb_streams(wd._driver.current_url):
        return df
    l = Logger()
    up_id = match_ytb_upid(wd._driver.current_url)
    ytb_scroll_to_bottom(wd)
    nodes = wd.xpath_wait("//ytd-rich-item-renderer")
    for i, node in enumerate(reversed(nodes)):
        print(
            f"\r解析当前页的视频列表：{float((i+1) / len(nodes)) * 100:.2f}%", end="" if i + 1 != len(nodes) else "\n"
        )
        info = []
        cols = []
        try:
            _nodes = xpath(node, "./div/yt-lockup-view-model/div/a[@class='ytLockupViewModelContentImage']")
            if len(_nodes):
                v_id = match_ytb_vid_byUrl(str(_nodes[0].get_attribute("href")))
                info.append(v_id)
                cols.append("v_id")
                cover = f"https://i.ytimg.com/vi/{v_id}/hq720.jpg"
                info.append(cover)
                cols.append("cover")
                url = f"https://www.youtube.com/watch?v=" + v_id
                info.append(url)
                cols.append("url")
            info.append(ytbtype)
            cols.append("ytbtype")
            info.append(up_id)
            cols.append("up_id")
            title = xpath(
                node,
                ".//span[@class='ytAttributedStringHost ytAttributedStringWhiteSpacePreWrap']",
            )[0].text
            info.append(title)
            cols.append("title")

            upload_string = ""
            for _node in xpath(
                node,
                ".//span[@class='ytAttributedStringHost ytContentMetadataViewModelMetadataText ytContentMetadataViewModelMetadataTextLastPart ytAttributedStringWhiteSpacePreWrap ytAttributedStringLinkInheritColor']",
            ):
                if "前" in _node.text:
                    upload_string = _node.text
                    break
            info.append(parse_ytbUploadStamp(upload_string))
            cols.append("upload")

            play = 0
            _nodes = xpath(
                node,
                ".//span[@class='ytAttributedStringHost ytContentMetadataViewModelMetadataText ytAttributedStringWhiteSpacePreWrap ytAttributedStringLinkInheritColor']",
            )
            if len(_nodes):
                play = parse_ytbPlaytimes(_nodes[0].text)
            info.append(play)
            cols.append("play")

            duration = 0
            _nodes = xpath(node, ".//div[@class='ytBadgeShapeText']")
            if len(_nodes):
                duration = parse_ytbDuration(_nodes[0].text)
            info.append(duration)
            cols.append("duration")

            isCharge: bool = "会员专享" in node.text or "会员抢先观看" in node.text
            info.append(isCharge)
            cols.append("isCharge")

            info.append(get_timestamp())
            cols.append("data_time")
        except:
            print("+" * 80)
            print(f"ERROR: {i+1} / {len(nodes)} in {wd._driver.current_url}")
            traceback.print_exc()
            print("+" * 80)
            l.error(f"ERROR: {i+1} / {len(nodes)} in {wd._driver.current_url}")
            l.error(traceback.format_exc())
        tmp_df = pandas.DataFrame(data=[info], columns=cols)
        df = pandas.concat([df, tmp_df])
    return df


def task_update_ytb_database(urls: list, db_fp: str):
    """更新数据库"""
    if len(urls) == 0 or db_fp == "":
        return
    db = DataBase()
    if db.isConnected:
        db.Disconnect()
    db.Connect(db_fp)
    wd = MyWebDriver()
    wd.selenium_options.append("--force-dark-mode")
    wd.selenium_options.append("--mute-audio")
    wd._generate_driver()
    # wd._driver.set_page_load_timeout(60)
    l = Logger()
    for index, url in enumerate(urls):
        print("\n\n" + "=" * 80 + "\n")
        l.info(f"{index+1} / {len(urls)} : {url}")
        wd.Goto(url)
        time.sleep(10)
        wd.setTabPageTitle(f"{index+1} / {len(urls)} " + wd._driver.title)
        parse_YtbUp(wd, db, ["视频", "直播"])

    wd.Quit()
    db.Disconnect()
