import re
import pandas as pd
import traceback
from Web.MyWebDriver import *
from Web.biliPlayListParse import *
from Common.match_bili import *
from Common.Logger import *
from DataAccess.sql_bilibili import *

videoinfo_xpath = '//div[@class="bili-video-card__wrap"]'


def if404(wd: MyWebDriver) -> bool:
    return len(wd.xpath_wait('//div[@class="code" and contains(text(), "错误码：-404")]')) != 0


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

        node = wd.xpath_wait("//meta[@data-vue-meta and contains(@content, 'jpg')]")[0]
        cover = node.get_attribute("content")
        info.append(cover)
        columns.append("cover")
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
                match = re.match(r"https://www.bilibili.com/video/([0-9a-zA-Z]*)/.*", href)
                if match:
                    v_id = match.group(1)
                    if v_id:
                        info.append(v_id)
                        columns.append("v_id")

            _node = xpath(node, './/div[@class="info"]/div[@class="upname"]/a[@href]')[0]
            space = _node.get_attribute("href")
            if space:
                match = re.match(r"https://space.bilibili.com/([0-9]*)/.*", space)
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
    time.sleep(5)
    wd.xpath_wait(videoinfo_xpath)
    wd.xpath_wait("//div[@class='b-avatar__layer__res']//source[@type='image/webp' and @srcset]")
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

        url = f"https://space.bilibili.com/{up_id}/upload/video"
        info.append(url)
        columns.append("url")

        up_name = wd.xpath_findall('//div[@class="nickname"]')[0].get_attribute("textContent")
        info.append(up_name)
        columns.append("up_name")

        intro = wd.xpath_findall('//div[@class="pure-text" and @title]')[0].get_attribute("title")
        info.append(intro)
        columns.append("intro")

        up_sum_string = wd.xpath_findall("//div[@class='side-nav__item__sub']")[0].text
        try:
            up_sum = int(up_sum_string.split(" ")[0])
        except:
            up_sum = 10000  # TODO 解析大于10000的字符串
        info.append(up_sum)
        columns.append("up_sum")

        facenodes = wd.xpath_wait("//div[@class='b-avatar__layer__res']//source[@type='image/webp' and @srcset]")
        if len(facenodes):
            face = facenodes[0].get_attribute("srcset")
            if face:
                face = face.split("@")[0]
                face = f"https:{face}"
            info.append(face)
            columns.append("face")

        nodes = wd.xpath_findall(videoinfo_xpath)

        up_last_vid = biliurl2BV(xpath(nodes[0], "./div/div/a")[0].get_attribute("href"))
        info.append(up_last_vid)
        columns.append("up_last_vid")

        date_string = xpath(nodes[0], './/div[@class="bili-video-card__subtitle"]')[0].get_attribute("textContent")
        p = -1
        if date_string:
            p = parse_upload_timestamp(date_string)
        info.append(p)
        columns.append("up_last_time")

    except:
        print("+" * 80)
        print(f"{wd._driver.current_url}")
        traceback.print_exc()
        print("+" * 80)
    df = pd.DataFrame([info], columns=columns)
    return df


def task_bili_update_all(urls: list, db_fp: str):
    """要求能够作为任务添加到processmanager"""
    if len(urls) == 0:
        return
    db = DataBase()
    if db.isConnected:
        db.Disconnect()
    db.Connect(db_fp)
    wd = MyWebDriver()
    wd.selenium_options.append("--force-dark-mode")
    wd.selenium_options.append("--mute-audio")
    wd.Login()
    wd._driver.minimize_window()
    l = Logger()
    for index, url in enumerate(urls):
        print("\n\n" + "=" * 80 + "\n")
        l.info(f"{index+1} / {len(urls)} : {url}")
        wd.Goto(url)
        time.sleep(3)
        wd.setTabPageTitle(f"{index+1} / {len(urls)} " + wd._driver.title)
        wd.xpath_wait(videoinfo_xpath)
        insert_up(db, parse_spacePage(wd))
        up_id = str(match_upspace(wd._driver.current_url))
        l.info(f"该up视频总数应为：\t{int(get_up_info(db, up_id).iloc[0]['up_sum'])}")
        l.info(f"现有视频总数为：\t{len(get_allvideoinfo_byupid(db, up_id))}")
        maxresult = get_len_missingvideo(db, up_id)
        if maxresult > 0:
            l.info(f"该up缺少的视频数量为{maxresult}, 抓取指定数量的视频")
            insert_video(db, parse_multi_back_playlistPage(wd, maxresult))
            l.info(f"爬取后视频总数为：\t{len(get_allvideoinfo_byupid(db, up_id))}")

        for i in range(3):  # TODO magic number
            ret = judge_bilibiliUP_needupdate(db, up_id)
            if ret == 0:
                break
            l.info(f"up主 {url} 的视频重新爬取, 状况为：{ret}")
            delete_allvideo_byupid(db, up_id)
            wd._driver.refresh() # 刷新以前往分页第一页
            time.sleep(3)
            wd.setTabPageTitle(f"{index+1} / {len(urls)} " + wd._driver.title)
            insert_video(db, parse_multi_back_playlistPage(wd))
            l.info(f"再次爬取后数据库总数：\t{len(get_allvideoinfo_byupid(db, up_id))}")

    wd.Quit()
    db.Disconnect()
