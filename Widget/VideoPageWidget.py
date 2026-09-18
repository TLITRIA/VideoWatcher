from UI.videoPageForm import Ui_Form
import pandas as pd
from PyQt6.QtWidgets import QWidget, QScrollArea, QListWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal
from Common.PyQt import *
from Common.FlowLayout import *
from Web.MyWebDriver import *
from Web.biliParse import *
from Widget.UrlWidget import UrlWidget
from Widget.InfoWidget import InfoWidget
from DataAccess.DataBase import *
from DataAccess.sql_query import *


class VideoPageWidget(QWidget, Ui_Form): # VideoPage
    db: DataBase = DataBase()
    wd: MyWebDriver = MyWebDriver()
    s_goto = pyqtSignal(str)

    def __init__(self, parent=None):
        super(VideoPageWidget, self).__init__(parent)
        self.setupUi(self)

        self.scrollArea.setWidgetResizable(True)
        container = QWidget()
        self.flow_layout = FlowLayout(container, margin=10, spacing=10)
        self.scrollArea.setWidget(container)
        

    def updateData(self):
        # 1. 更新视频信息
        infow = InfoWidget(self)
        infow.series_update_all(parse_videoPage().iloc[0])
        infow.s_goto_upspace.connect(lambda url: self.s_goto.emit(url))
        infow.s_goto_videopage.connect(lambda url: self.s_goto.emit(url))
        # 2. 更新相关视频
        df = parse_videoPage_related()
        self.remove_allFlowLayout()
        for i in range(len(df)):
            w = InfoWidget(self)
            face = ""
            up_df = get_up_info(self.db, df["up_id"].iloc[i])
            if up_df.shape[0] > 0:
                face = up_df["face"].iloc[0]
            tmp_series = df.iloc[i]
            # tmp_df = df.iloc[i:i+1, :]
            tmp_series["face"] = face
            w.series_update_all(tmp_series)
            w.setFixedSize(260, 155)
            self.flow_layout.addWidget(w)
            w.s_goto_upspace.connect(lambda url: self.s_goto.emit(url))
            w.s_goto_videopage.connect(lambda url: self.s_goto.emit(url))
        # 3. 更新视频链接
        urls = []
        intro = parse_videoPage_intro(self.wd)
        for line in intro.split("\n"):
            line = line.strip()
            if line.startswith("https://"):
                urls.append(line)
        self.update_urls(urls)

    def update_urls(self, urls: list[str]):
        self.list_goto.clear()
        for url in urls:
            w = UrlWidget(url, self)
            w.s_goto.connect(lambda url: self.s_goto.emit(url))
            w.show()
            item = QListWidgetItem(self.list_goto)
            item.setSizeHint(w.sizeHint())
            self.list_goto.addItem(item)
            self.list_goto.setItemWidget(item, w)

    def remove_allFlowLayout(self):
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
