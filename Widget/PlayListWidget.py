from UI.biliPlaylistForm import Ui_Form
import os, sys
import pandas as pd
from os.path import abspath

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIcon, QCursor
from PyQt6.QtCore import pyqtSignal, Qt, QStringListModel
from DataAccess.DataBase import *
from DataAccess.sql_query import *
from Common.PyQt import *
from Common.FlowLayout import *
from Common.Process import *
from Web.MyWebDriver import *
from Web.biliParse import *
from Web.biliPlayListParse import *
from Widget.InfoWidget import InfoWidget
from Widget.InfoFuncDialog import *


class PlayListWidget(QWidget, Ui_Form):
    wd = MyWebDriver()
    df = pd.DataFrame()
    s_goto = pyqtSignal(str)

    def on_input_url(self):  # 输入收藏夹url
        url = self.line_input.text()
        self.line_input.clear()
        self.wd.Goto(url)
        self.update_playlist()

    def on_click_toolbut(self, w: InfoWidget):
        d = InfoFuncDialog(w)
        d.move(QCursor.pos())
        d.exec()

    def on_click_current(self):
        self.wd.Focus()
        if match_playlist(self.wd._driver.current_url):
            self.wd._driver.refresh()
            self.update_playlist()

    def on_click_cleanFlowlayout(self):
        data = []
        for i in range(self.flow_layout.count()-1, -1, -1):
            item = self.flow_layout.itemAt(i)
            if not item:
                continue
            w: InfoWidget = item.widget()
            if exist_up(DataBase(), w._up_id) or exclude_up(
                DataBase(), w._up_id
            ):
                data.append([w._v_id, w._fold_name])
                w.s_del_infoW.emit(w)
        pm = ProcessManager()
        pm.AddTask(remove_video_fromFold, *[data])
        # remove_video_fromFold(data)

    def del_infoW(self, w: InfoWidget):
        self.flow_layout.removeWidget(w)
        w.isDeleted = True
        w.deleteLater()
        self.update_playlist_number()
        
    def __init__(self, parent=None):
        super(PlayListWidget, self).__init__(parent)
        self.setupUi(self)
        self.scrollArea.setWidgetResizable(True)

        container = QWidget()
        self.flow_layout = FlowLayout(container, margin=10, spacing=10)
        self.scrollArea.setWidget(container)
        self.update_playlist_number()

    def update_playlist(self):
        playlist_df = parse_multi_playlistPage()
        self.remove_allFlowLayout()
        for i in range(len(playlist_df)):
            w = InfoWidget(self)

            face = ""
            up_df = get_up_info(DataBase(), playlist_df["up_id"].iloc[i])
            if up_df.shape[0]:
                face = up_df["face"][0]

            df = playlist_df.iloc[i]  
            df['face'] = face
            args = [
                playlist_df["v_id"].iloc[i],
                playlist_df["up_id"].iloc[i],
                playlist_df["title"].iloc[i],
                playlist_df["up_name"].iloc[i],
                face,
                playlist_df["cover"].iloc[i],
            ]
            w.series_update_all(df)
            w.set_fold_name(playlist_df["fold_name"].iloc[i])
            w.setFixedSize(260, 155)
            self.flow_layout.addWidget(w)

            w.s_toolbar.connect(self.on_click_toolbut)
            w.s_goto_upspace.connect(lambda url: self.s_goto.emit(url))
            w.s_goto_videopage.connect(lambda url: self.s_goto.emit(url))
            w.s_del_infoW.connect(self.del_infoW)
        self.update_playlist_number()

    def remove_allFlowLayout(self):
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self.update_playlist_number()

    def update_playlist_number(self):
        n = self.flow_layout.count()
        self.label.setText(f"共计 {n} 个结果")
