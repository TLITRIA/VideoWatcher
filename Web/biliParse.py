import re
import pandas as pd
import traceback
from Web.MyWebDriver import *
from Web.BackWebDriver import *
from Web.biliPlayListParse import *

from Common.BiliBili import *
from DataAccess.sql_query import *

videoinfo_xpath = '//div[@class="bili-video-card__wrap"]'


def if404(wd: MyWebDriver) -> bool:
    return (
        len(
            wd.xpath_wait(
                '//div[@class="code" and contains(text(), "错误码：-404")]'
            )
        )
        != 0
    )


def parse_videoPage() -> pd.DataFrame:
    """
    视频播放页
    视频本身的信息
    """
    wd = MyWebDriver()
    df = pd.DataFrame()
    info = []
    columns = []
    try:
        match = re.match(
            r"https://www.bilibili.com/video/([0-9a-zA-Z]*)/.*",
            wd._driver.current_url,
        )
        if match:
            v_id = match.group(1)
            info.append(v_id)
            columns.append("v_id")

        node = wd.xpath_wait("//div[@class='up-detail-top']/a")[0]
        up_id = node.get_attribute("href")
        if up_id:
            match = re.match(r"https://space.bilibili.com/([0-9]*)/.*", up_id)
            if match:
                up_id = match.group(1)
        info.append(up_id)
        columns.append("up_id")

        up_name = node.text.strip()
        info.append(up_name)
        columns.append("up_name")

        video_intro = ""
        nodes = wd.xpath_wait('//span[@class="desc-info-text"]')
        if len(nodes) > 0:
            video_intro = nodes[0].text
        info.append(video_intro)
        columns.append("video_intro")

        title = ""
        node = wd.xpath_findall("//h1[@data-title]")[0]
        title = node.get_attribute("data-title")
        info.append(title)
        columns.append("title")

        node = wd.xpath_wait(
            "//meta[@data-vue-meta and contains(@content, 'jpg')]"
        )[0]
        cover = node.get_attribute("content")
        info.append(cover)
        columns.append("cover")

        # upload
        # play
        # danmu
        # duration
        # isCharge
        # data_time
    except:
        print("-" * 80)
        traceback.print_exc()
    df = pd.DataFrame([info], columns=columns)
    return df


def parse_videoPage_face() -> str:
    wd = MyWebDriver()
    try:
        node = wd.xpath_wait("//img[@data-src]")[1]
        if node:
            url = node.get_attribute("data-src")
            if url:
                url = "https:" + url.split("@")[0]
                return url
    except:
        pass
    return ""


def parse_videoPage_vid() -> str:
    wd = MyWebDriver()
    vid = ""
    try:
        match = re.match(
            r"https://www.bilibili.com/video/([0-9a-zA-Z]*)/.*",
            wd._driver.current_url,
        )
        if match:
            vid = match.group(1)
    except:
        pass
    return vid


def parse_videoPage_upid(wd=None) -> str:
    if wd is None:
        wd = MyWebDriver()
    node = wd.xpath_wait("//div[@class='up-detail-top']/a")[0]
    up_id = node.get_attribute("href")
    if up_id:
        match = re.match(r"https://space.bilibili.com/([0-9]*)/.*", up_id)
        if match:
            up_id = match.group(1)
            return up_id
    return ""


def parse_videoPage_related() -> pd.DataFrame:
    wd = MyWebDriver()
    df = pd.DataFrame()
    info = []
    columns = []
    try:
        # 点击展开
        time.sleep(2)
        but = wd.xpath_wait("//div[@class='rec-footer']")[0]
        wd.ClickNode(but)
        wd.ScrollToBottomAndBack()
        wd.xpath_wait("//img")
        nodes = wd.xpath_wait('//div[@class="video-page-card-small"]')
        for index, node in enumerate(nodes):
            info = []
            columns = []

            _node = xpath(node, './/div[@class="info"]/a[@href]')[0]
            href = _node.get_attribute("href")
            if href:
                match = re.match(
                    r"https://www.bilibili.com/video/([0-9a-zA-Z]*)/.*", href
                )
                if match:
                    v_id = match.group(1)
                    if v_id:
                        info.append(v_id)
                        columns.append("v_id")

            _node = xpath(
                node, './/div[@class="info"]/div[@class="upname"]/a[@href]'
            )[0]
            space = _node.get_attribute("href")
            if space:
                match = re.match(
                    r"https://space.bilibili.com/([0-9]*)/.*", space
                )
                if match:
                    up_id = match.group(1)
                    if up_id:
                        info.append(up_id)
                        columns.append("up_id")

            up_name = _node.text
            info.append(up_name)
            columns.append("up_name")

            _node = xpath(node, './/div[@class="info"]/a[@href]')[0]
            title = _node.text
            info.append(title)
            columns.append("title")

            _node = xpath(node, ".//img")[0]
            cover = _node.get_attribute("src")
            if cover:
                cover = cover.split("@")[0]
            info.append(cover)
            columns.append("cover")

            df = pd.concat([df, pd.DataFrame([info], columns=columns)])
    except:
        print("-" * 80)
        traceback.print_exc()
    return df


def parse_videoPage_intro(wd: MyWebDriver) -> str:
    intro = ""
    try:
        nodes = wd.xpath_wait("//span[@class='desc-info-text']")
        if len(nodes) == 1:
            intro = nodes[0].text
    except:
        print("-" * 80)
        traceback.print_exc()
    return intro


def parse_spacePage(wd=None) -> pd.DataFrame:
    df = pd.DataFrame()
    if wd is None:
        wd = MyWebDriver()
    info = []
    columns = []
    wd.xpath_wait(videoinfo_xpath)
    try:
        data_time = get_timestamp()
        info.append(data_time)
        columns.append("data_time")

        up_id = match_upspace(wd._driver.current_url)
        if up_id:
            info.append(up_id)
            columns.append("up_id")
        else:
            print("未访问空间视频页")
            return df

        up_name = wd.xpath_findall(
            '//div[@data-v-72f03be2 and @class="nickname"]'
        )[0].get_attribute("textContent")
        info.append(up_name)
        columns.append("up_name")

        intro = wd.xpath_findall(
            '//div[@data-v-9b33e4bd and @class="pure-text" and @title]'
        )[0].get_attribute("title")
        info.append(intro)
        columns.append("intro")

        up_sum_string = wd.xpath_findall("//div[@class='side-nav__item__sub']")[
            0
        ].text
        try:
            up_sum = int(up_sum_string.split(" ")[0])
        except:
            up_sum = 10000  # TODO 解析大于10000的字符串
        info.append(up_sum)
        columns.append("up_sum")

        face = wd.xpath_wait(
            "//div[@class='b-avatar__layer__res']//source[@type='image/webp' and @srcset]"
        )[0].get_attribute("srcset")
        if face:
            face = face.split("@")[0]
            face = f"https:{face}"
        info.append(face)
        columns.append("face")

        nodes = wd.xpath_findall(videoinfo_xpath)
        # upload_lasttitle = xpath(
        #     nodes[0], './/div[@class="bili-video-card__title"]'
        # )[0].get_attribute("title")
        # info.append(upload_lasttitle)
        # columns.append("upload_lasttitle")

        up_last_vid = biliurl2BV(
            xpath(nodes[0], "./div/div/a")[0].get_attribute("href")
        )
        info.append(up_last_vid)
        columns.append("up_last_vid")

        date_string = xpath(
            nodes[0], './/div[@class="bili-video-card__subtitle"]'
        )[0].get_attribute("textContent")
        # date_stamp = bili_datestringParse(date_string)
        info.append(date_string)
        columns.append("up_last_time")

    except:
        traceback.print_exc()
    df = pd.DataFrame([info], columns=columns)
    # print(df)
    return df


def back_update_up(urls: list):
    """
    按照提供的up主视频页列表更新up主信息
    """
    if len(urls) == 0:
        return
    bd: BackWebDriver = BackWebDriver()
    db = DataBase()
    db.Connect(videowatcher_sql_fp)
    if "--headless" in bd.selenium_options:
        bd.selenium_options.remove(
            "--headless"
        ) 
    bd.Login()

    for index, url in enumerate(urls):
        try:
            print(f"进度条：{index+1}/{len(urls)}")
            bd.Goto(url)
            up_insert(db, parse_spacePage(bd))
            bd.xpath_wait(videoinfo_xpath)
            time.sleep(1)
        except:
            print(f"第 {index+1} 个up主 {url} 抓取失败")
    bd.Quit()
    if len(get_up_id_whichvideoisnotnew(db)) > 0:
        print("up主未能更新最新视频")  # TODO: 通知


def back_update_video(urls: list):
    if len(urls) == 0:
        return
    bd: BackWebDriver = BackWebDriver()
    db = DataBase()
    db.Connect(videowatcher_sql_fp)
    if "--headless" in bd.selenium_options:
        bd.selenium_options.remove("--headless")
    bd.Login()

    for index, url in enumerate(urls):
        bd.Goto(url)
        time.sleep(1)
        maxresult = 0
        up_id = str(match_upspace(bd._driver.current_url))
        try:
            maxresult = get_len_missingvideo(db, up_id)
        except:
            pass
        print(f"{index+1} / {len(urls)} : {url}")
        print(f"该up缺少的视频数量为{maxresult}, 抓取指定数量的视频")
        df = parse_multi_back_playlistPage(bd, maxresult)
        video_insert(db, df)
        if get_len_missingvideo(db, up_id) > 0:# 出现这种情况意味着可能中间有视频未抓取或者失效，需要完整地爬取
            print(f"up主 {url} 的视频没有全部抓取到")
            # TODO 清空该up的视频
            bd.Goto(url)
            time.sleep(1)
            df = parse_multi_back_playlistPage(bd)
            video_insert(db, df)
    bd.Quit()
