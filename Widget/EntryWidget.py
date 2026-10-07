from UI.entryForm import Ui_Form
import re
import random
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
from Web.ytbParse import *
from Common.match_bili import *
from Common.Process import *
from DataAccess.sql_bilibili import *


class EntryWidget(QWidget, Ui_Form):
    _wd = MyWebDriver()
    _db = DataBase()

    def on_update_fillup(self):
        if not self._db.isConnected:
            return
        urls = [f"https://space.bilibili.com/{x}/upload/video" for x in get_up_unfilled(self._db)]
        random.shuffle(urls)
        if len(urls) > 0:
            pm = ProcessManager()
            pm.AddTask(task_bili_update_all, *[urls, default_db_fp, False])

    def on_update_allup(self):
        if not self._db.isConnected:
            return
        urls = [f"https://space.bilibili.com/{x}/upload/video" for x in get_all_up_id(self._db, "up")]
        random.shuffle(urls)
        if len(urls) > 0:
            pm = ProcessManager()
            pm.AddTask(task_bili_update_all, *[urls, default_db_fp, False])

    def on_click_bilibili_rebuild(self):
        if not self._db.isConnected:
            return
        up_ids = []
        for i, up_id in enumerate(get_all_up_id(self._db, "up")):
            ret = judge_bilibiliUP_needupdate(self._db, up_id)  # 减少工作量
            if ret != 0:
                up_ids.append(up_id)
        urls = [f"https://space.bilibili.com/{x}/upload/video" for x in up_ids]
        random.shuffle(urls)
        if len(urls) > 0:
            pm = ProcessManager()
            pm.AddTask(task_bili_update_all, *[urls, default_db_fp, True])

    def on_click_ytb_fillup(self):
        if not self._db.isConnected:
            return
        urls = [f"https://www.youtube.com/@{x}" for x in ytb_get_up_unfilled(self._db)]
        random.shuffle(urls)
        if len(urls) > 0:
            pm = ProcessManager()
            pm.AddTask(task_update_ytb_database, *[urls, default_db_fp, []])

    def on_click_ytb_allup(self):
        if not self._db.isConnected:
            return
        urls = [f"https://www.youtube.com/@{x}" for x in get_all_up_id(self._db, "ytbup")]
        random.shuffle(urls)
        if len(urls) > 0:
            pm = ProcessManager()
            pm.AddTask(task_update_ytb_database, *[urls, default_db_fp, []])

    def on_click_ytb_rebuild(self):
        if not self._db.isConnected:
            return
        up_ids = []
        for i, up_id in enumerate(get_all_up_id(self._db, "ytbup")):
            ret = judge_ytbUp_needupdate(self._db, up_id)  # 减少工作量
            if ret != 0:
                up_ids.append(up_id)
        urls = [f"https://www.youtube.com/@{x}" for x in up_ids]
        random.shuffle(urls)
        if len(urls) > 0:
            pm = ProcessManager()
            pm.AddTask(task_update_ytb_database, *[urls, default_db_fp])

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
            w.series_update_all(parse_spacePage(self._wd).iloc[0])
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
            w.showMaximized()
            w.update_playlist()
            return
        print(f"未解析到页面: {url}")
        return
        match = re.match(r"(https://www.bilibili.com/video/[0-9a-zA-Z]*).*", url)
        if match:
            url = match.group(1)
            self.stackedWidget.setCurrentIndex(0)
            vw: VideoPageWidget = self.subWidgets[0]
            vw.updateData()
            self.label.setText(self.title[0])
            return
        match = re.match(r"(https://space.bilibili.com/[0-9]*/upload/video)", url)
        if match:
            url = match.group(1)
            self.stackedWidget.setCurrentIndex(1)
            uw: UpWidget = self.subWidgets[1]
            uw.updateData()
            self.label.setText(self.title[1])
            return
        match = re.match(r"(https://www.youtube.com/watch?v=[0-9a-zA-Z]*).*", url)
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
