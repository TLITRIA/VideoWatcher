from UI.entryForm import Ui_Form
import re
from PyQt6.QtWidgets import QWidget, QListWidgetItem
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSignal, Qt
from Widget.VideoPageWidget import VideoPageWidget
from Widget.InfoWidget import InfoWidget
from Widget.PlayListWidget import PlayListWidget
from Widget.DbWidget import DbWidget
from Web.MyWebDriver import MyWebDriver
from Web.biliParse import *
from Web.biliAccess import *
from Common.BiliBili import *
from Common.Process import *
from DataAccess.sql_query import *


class EntryWidget(QWidget, Ui_Form):
    _wd = MyWebDriver()

    # def goto(self, url: str):
    #     # self._wd.Focus()  # 为什么要添加这个？
    #     self._wd.Goto(url)
    #     self.focus()

    def on_update_fillup(self):
        up_ids = get_up_unfilled(DataBase())
        urls = []
        for up_id in up_ids:
            urls.append(f"https://space.bilibili.com/{up_id}/upload/video")
        urls = list(set(urls))
        pm = ProcessManager()
        pm.AddTask(back_update_up, *[urls])

    def on_update_allup(self):
        up_ids = get_all_up_id(DataBase())
        urls = []
        for up_id in up_ids:
            urls.append(f"https://space.bilibili.com/{up_id}/upload/video")
        urls = list(set(urls))
        pm = ProcessManager()
        pm.AddTask(back_update_up, *[urls])

    def on_update_fillvideo(self):
        up_ids = get_up_id_whichvideoisnotnew(DataBase())
        urls = []
        for up_id in up_ids:
            urls.append(f"https://space.bilibili.com/{up_id}/upload/video")
        urls = list(set(urls))
        pm = ProcessManager()
        pm.AddTask(back_update_video, *[urls])

    def on_update_allvideo(self):
        up_ids = get_all_up_id(DataBase())
        urls = []
        for up_id in up_ids:
            urls.append(f"https://space.bilibili.com/{up_id}/upload/video")
        urls = list(set(urls))
        pm = ProcessManager()
        pm.AddTask(back_update_video, *[urls])

    def on_click_defaultplaylist(self):
        goto_default_collectfolder(self._wd)
        self.focus()

    def on_click_dbview(self):
        self.dbw = DbWidget()  # w 的生命周期
        self.dbw.show()

    def __init__(self, parent=None):
        super(EntryWidget, self).__init__(parent)
        self.setupUi(self)

    def focus(self):
        self._wd.FocusHead()
        url = self._wd._driver.current_url
        if match_upspace(url):  # bilibili up主视频页
            w = InfoWidget()
            w.series_update_all(parse_spacePage().iloc[0])
            w.s_goto_videopage.connect(lambda url: self._wd.Goto(url))
            w.s_goto_upspace.connect(lambda url: self._wd.Goto(url))
            w.show()
            return
        elif match_video(url):  # bilibili视频页
            w = VideoPageWidget()
            w.updateData()
            w.s_goto.connect(lambda url: self._wd.Goto(url))
            w.show()
            return
        elif match_playlist(url):
            w = PlayListWidget()
            w.s_goto.connect(lambda url: self._wd.Goto(url))
            w.update_playlist()
            w.show()
            return
        print(f"未解析到页面: {url}")
        return
        match = re.match(
            r"(https://www.bilibili.com/video/[0-9a-zA-Z]*).*", url
        )
        if match:
            url = match.group(1)
            self.stackedWidget.setCurrentIndex(0)
            vw: VideoPageWidget = self.subWidgets[0]
            vw.updateData()
            self.label.setText(self.title[0])
            return
        match = re.match(
            r"(https://space.bilibili.com/[0-9]*/upload/video)", url
        )
        if match:
            url = match.group(1)
            self.stackedWidget.setCurrentIndex(1)
            uw: UpWidget = self.subWidgets[1]
            uw.updateData()
            self.label.setText(self.title[1])
            return
        match = re.match(
            r"(https://www.youtube.com/watch?v=[0-9a-zA-Z]*).*", url
        )
        if match:
            url = match.group(1)
            # self.update_ytbvideo()
            return
        match = re.match(r"(https://www.youtube.com/@.*)", url)
        if match:
            url = match.group(1)
            # self.update_ytbspace()
            return
        print(url)  # 未解析出的链接
