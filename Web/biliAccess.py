from Web.MyWebDriver import *
from Web.BackWebDriver import *
import time


def remove_video_fromFold(datalist) -> bool:
    WD = BackWebDriver()   
    WD.Login()
    
    for index, [video_id, fold_id] in enumerate(datalist):
        print(f"正在处理第{index+1}个视频")

        if not video_id or not fold_id:
            continue
        url = f"https://www.bilibili.com/video/{video_id}/"
        if not WD._driver.current_url.startswith(url):
            WD.Goto(url)
            time.sleep(3)

        nodes = WD.xpath_wait("//div[@title='收藏（E）']")
        if nodes:
            WD.ClickNode(nodes[0])
            time.sleep(1)
        else:
            continue
        nodes = WD.xpath_wait('//div/ul/li/label[./input[@type="checkbox"]]')
        if nodes:
            for node in nodes:
                _nodes = xpath(node, './input[@type="checkbox"]')
                if _nodes and _nodes[0].is_selected() and fold_id in node.text:
                    WD.ClickNode(_nodes[0])
                    time.sleep(0.5)
            but_comfirm = WD.xpath_findall(
                "//button[contains(text(), '确定')]"
            )[0]
            WD.ClickNode(but_comfirm)
            time.sleep(1)
    WD.Quit()
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
