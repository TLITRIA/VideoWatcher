import re
import pandas as pd
import traceback
from Web.MyWebDriver import *
from Common.Logger import timeblock
from Common.BiliBili import *

videoinfo_xpath = '//div[@class="bili-video-card__wrap"]'


def parse_current_playlistPage(wd=None) -> pd.DataFrame:
    """
    解析当前播放列表页面
    :param wd: WebDriver
    :return: DataFrame
    """
    if wd is None:
        wd = MyWebDriver()
    df = pd.DataFrame()
    # print('-'*80)
    # with timeblock("step1 : wait"):
    tmp_count = 0
    nodes = wd.xpath_wait(videoinfo_xpath)
    wd.xpath_wait('//a[@class="bili-cover-card"]')
    wd.xpath_wait('//div[@class="bili-video-card__text"]')
    wd.xpath_wait('//a[@class="bili-video-card__author"]')
    while len(nodes) == 0:
        nodes = wd.xpath_wait(videoinfo_xpath)
        tmp_count += 1
        if tmp_count == 3:
            wd._driver.refresh()
        if tmp_count > 6:
            return df
    fold_name = ""
    # with timeblock("step2: fold_name"):
    fold_name = "默认收藏夹"
    match = re.match(r".*fid=([0-9]*)&ftype=create", wd._driver.current_url)
    if match:
        fold_nodes = wd.xpath_findall(f'//div[@class="fav-sidebar-item" and @id="{match.group(1)}"]')
        if len(fold_nodes):
            fold_name = fold_nodes[0].get_attribute("title")

    for index, node in enumerate(nodes):  # //div[@class="bili-video-card__wrap"]
        # with timeblock(f"step3: parse {index} node"):
        try:
            tmp_df = pd.DataFrame()
            info = []
            columns = []

            _node = xpath(node, './/a[@class="bili-cover-card"]')[0]
            href = _node.get_attribute("href")
            if href:
                match = re.match(r"https://www.bilibili.com/video/([0-9a-zA-Z]*).*", href)
                if match:
                    v_id = match.group(1)
                    info.append(v_id)
                    columns.append("v_id")

            _node = xpath(node, './/a[@class="bili-video-card__author"]')[0]
            href = _node.get_attribute("href")
            if href:
                match = re.match(r"https://space.bilibili.com/([0-9a-zA-Z]*).*", href)
                if match:
                    up_id = match.group(1)
                    info.append(up_id)
                    columns.append("up_id")
            _node = xpath(node, './/div[@class="bili-video-card__text"]/span')[-1]
            up_name = _node.text
            if up_name:
                up_name = up_name.split(" · ")[0]
                info.append(up_name)
                columns.append("up_name")

            _node = xpath(node, './/div[@class="bili-cover-card__thumbnail"]/img')[0]
            cover = _node.get_attribute("src")
            if cover:
                cover = cover.split("@")[0]
                info.append(cover)
                columns.append("cover")

            title = _node.get_attribute("alt")
            if title:
                info.append(title)
                columns.append("title")

            info.append(fold_name)
            columns.append("fold_name")

            tmp_df = pd.DataFrame([info], columns=columns)
            df = pd.concat([df, tmp_df])
        except:
            traceback.print_exc()
    return df


def parse_other_playlistPage(wd=None) -> pd.DataFrame:
    """
    解析当前播放列表页面
    由于是他人的播放列表，不需要解析列表名称
    :param wd: WebDriver
    :return: DataFrame
    """
    if wd is None:
        wd = MyWebDriver()
    df = pd.DataFrame()
    tmp_count = 0

    nodes = wd.xpath_wait(videoinfo_xpath)
    while len(nodes) == 0:
        nodes = wd.xpath_wait(videoinfo_xpath)
        tmp_count += 1
        if tmp_count == 3:
            wd._driver.refresh()
        if tmp_count > 6:
            print("页面解析失败，疑似404")
            return df

    time.sleep(3)  # TODO 固定延时能不能缩短
    # wd.xpath_wait('//a[@target="_blank"]')
    # wd.xpath_wait('//div[@class="bili-video-card__title"]')
    # wd.xpath_wait("//img")
    # wd.xpath_wait('//div/div[@class="bili-cover-card__stat"]')
    # wd.xpath_wait('//div[@class="bili-video-card__wrap"]//a[@target="_blank" and @href]')

    nodes = wd.xpath_wait(videoinfo_xpath)
    up_id = match_upspace(wd._driver.current_url)
    for index, node in enumerate(nodes):  # //div[@class="bili-video-card__wrap"]
        try:
            tmp_df = pd.DataFrame()
            info = []
            columns = []
            _node = xpath(node, './/a[@target="_blank" and @href]')[0]
            href = _node.get_attribute("href")
            if href:
                match = re.match(r"https://www.bilibili.com/video/([0-9a-zA-Z]*).*", href)
                if match:
                    v_id = match.group(1)
                    info.append(v_id)
                    columns.append("v_id")

                    url = f"https://www.bilibili.com/video/{v_id}"
                    info.append(url)
                    columns.append("url")

            info.append(up_id)
            columns.append("up_id")

            title = xpath(node, './/div[@class="bili-video-card__title"]')[0].get_attribute("title")
            info.append(title)
            columns.append("title")

            cover = ""
            try:
                cover = xpath(node, ".//img")[0].get_attribute("src")
            except:
                pass
            if cover:
                cover = cover.split("@")[0]
            info.append(cover)
            columns.append("cover")

            upload = xpath(node, './/div[@class="bili-video-card__subtitle"]')[0].get_attribute("textContent")
            info.append(upload)
            columns.append("upload")

            pN, cN, dN = xpath(node, './/div/div[@class="bili-cover-card__stat"]')
            play = pN.get_attribute("textContent")
            if play:
                if "万" in play:
                    num = float(play.split("万")[0])
                    play = int(num * 1000)
                elif play == "NaN":
                    play = 0
                else:
                    play = int(play)
            danmu = cN.get_attribute("textContent")
            if danmu:
                if "万" in danmu:
                    num = float(danmu.split("万")[0])
                    danmu = int(num * 1000)
                else:
                    danmu = int(danmu)
            else:
                danmu = 0

            dt = dN.get_attribute("textContent")

            duration = 0
            if dt:
                dt = dt.strip()
                if len(dt) == 5:
                    duration = int(dt.split(":")[0]) * 60 + int(dt.split(":")[1])
                elif len(dt) == 8:
                    duration = int(dt.split(":")[0]) * 3600 + int(dt.split(":")[1]) * 60 + int(dt.split(":")[2])
            info.extend([play, danmu, duration])
            columns.extend(["play", "danmu", "duration"])

            info.append(1 if "充电专属" in str(node.get_attribute("textContent")) else 0)
            columns.append("isCharge")

            data_time = get_timestamp()
            info.append(data_time)
            columns.append("data_time")

            tmp_df = pd.DataFrame([info], columns=columns)
            df = pd.concat([df, tmp_df], ignore_index=True)
        except Exception as e:
            print("+" * 80)
            print(f"{index+1} / {len(nodes)}")
            traceback.print_exc()
            print("+" * 80)
    return df


but_下一页_xpath = '//button[@class and contains(text(), "下一页")]'


def get_biliPlaylist_nextbut(wd: MyWebDriver):
    """
    获取B站播放列表下一页按钮
    :param wd: WebDriver
    :return: WebElement
    """
    return wd.xpath_wait(but_下一页_xpath)


def df_concat(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    合并两个DataFrame
    :param df1: DataFrame
    :param df2: DataFrame
    :return: DataFrame
    """
    df = pd.concat([df1, df2])
    df.drop_duplicates(subset=["v_id"], keep="last", inplace=True)
    return df


def df_intersect(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
    """
    判断两个DataFrame是否有交集
    :param df1: DataFrame
    :param df2: DataFrame
    :return: bool
    """
    if df1.empty or df2.empty:
        return False
    else:
        common_set = set(df1["v_id"]) & set(df2["v_id"])
        return len(common_set) > 0


def parse_multi_playlistPage(wd=None, maxresult=200) -> pd.DataFrame:  # 默认读取少量信息
    """
    解析B站收藏夹列表
    :return: DataFrame
    """
    if wd is None:
        wd = MyWebDriver()
    df = pd.DataFrame()
    try:
        df = turning_page(
            wd,
            wd._driver.current_url,
            parse_current_playlistPage,
            get_biliPlaylist_nextbut,
            df_concat,
            df_intersect,
            maxresult,
        )
    except:
        print("-" * 80)
        traceback.print_exc()
    return df


def parse_multi_back_playlistPage(wd=None, maxresult=-1) -> pd.DataFrame:
    """
    解析B站播放列表页面
    :return: DataFrame
    """
    if wd is None:
        wd = MyWebDriver()
    df = pd.DataFrame()
    try:
        df = turning_page(
            wd,
            wd._driver.current_url,
            parse_other_playlistPage,
            get_biliPlaylist_nextbut,
            df_concat,
            df_intersect,
            maxresult,
        )
    except:
        print("-" * 80)
        traceback.print_exc()
    return df
