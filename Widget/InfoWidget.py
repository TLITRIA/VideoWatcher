from UI.infoFrom import Ui_Form
import os, sys
import pandas as pd
from os.path import abspath
from ipdb import set_trace as st

from PyQt6.QtWidgets import QWidget, QCompleter, QComboBox, QDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal, Qt, QStringListModel
from DataAccess.DataBase import *
from DataAccess.sql_query import *
from Common.BiliBili import *
from Common.PyQt import *
from Web.MyWebDriver import *
from Web.biliParse import *


def qcompleter_init(comp: QCompleter, tar: QComboBox):
    comp.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    comp.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
    comp.setFilterMode(Qt.MatchFlag.MatchContains)
    tar.setCompleter(comp)


class InfoWidget(QWidget, Ui_Form):
    _v_id: str = ""
    _up_id: str = ""
    _up_name: str = ""
    db: DataBase = DataBase()
    wd: MyWebDriver = MyWebDriver()

    isBlocked: bool = False
    isDeleted: bool = False
    up_select: list = []
    up_unselect: list = []
    v_select: list = []
    v_unselect: list = []

    s_toolbar = pyqtSignal(QWidget)  # 自定义工具对话框，内容什么由上一级控件决定
    s_del_infoW = pyqtSignal(QWidget)  # 删除控件的信号
    s_goto_upspace = pyqtSignal(str)  # 跳转up主页
    s_goto_videopage = pyqtSignal(str)  # 跳转视频页

    def slot_goto_video(self):
        if not self._v_id:
            return
        self.s_goto_videopage.emit(f"https://www.bilibili.com/video/{self._v_id}/")

    def slot_goto_space(self):
        if not self._up_id:
            return
        self.s_goto_upspace.emit(f"https://space.bilibili.com/{self._up_id}/upload/video")

    def on_video_add(self, i: int):
        tag = self.cb_add_v.currentText()
        self.cb_add_v.clearEditText()
        if not tag or tag in self.v_select or not self._v_id:
            return
        insert_video_tag(self.db, self._v_id, tag)
        self.update_video_tags()

    def on_video_del(self, i: int):
        tag = self.cb_del_v.currentText()
        self.cb_del_v.clearEditText()
        if not tag or tag in self.v_unselect or not self._v_id:
            return
        delete_video_tag(self.db, self._v_id, tag)
        self.update_video_tags()

    def on_up_tristate(self, state: Qt.CheckState):
        if self.isBlocked:
            return
        update_one_up_exclude(
            self.db,
            self._up_id,
            "",
            state == Qt.CheckState.Checked,
            f"https://space.bilibili.com/{self._up_id}/upload/video",
        )

        if state == Qt.CheckState.PartiallyChecked:
            if match_upspace(self.wd._driver.current_url):
                insert_up(self.db, parse_spacePage())
            else:
                insert_up_null(self.db, self._up_id)
        else:
            delete_up(self.db, self._up_id)
        self.im.update_up_collection(self._up_id, state)

    def on_up_add(self, i: int):
        tag = self.cb_add_up.currentText()
        self.cb_add_up.clearEditText()
        if not tag or tag in self.up_select or not self._up_id:
            return
        insert_up_tag(self.db, self._up_id, tag)
        self.update_up_tags()

    def on_up_del(self, i: int):
        tag = self.cb_del_up.currentText()
        if not tag or tag in self.up_unselect or not self._up_id:
            return
        delete_up_tag(self.db, self._up_id, tag)
        self.update_up_tags()

    def del_infoW(self):
        self.isDeleted = True
        self.s_del_infoW.emit(self)

    def __init__(self, parent=None):
        super(InfoWidget, self).__init__(parent)
        self.setupUi(self)
        # self.but_govideo.setIcon(QIcon(abspath_arrow))
        # self.but_gospace.setIcon(QIcon(abspath_arrow))
        self.cb_add_up.setEditable(True)
        # self.cb_add_up.setPlaceholderText("添加用户标签")
        self.cb_add_v.setEditable(True)
        # self.cb_add_v.setPlaceholderText("添加视频标签")

    def __del__(self):  # TODO 是否有这个函数？
        self.im.REMOVE(self)  # 从同步中删除

    def series_update_all(self, series: pd.Series):
        self.update_all(
            v_id=("" if "v_id" not in series.index.tolist() else str(series["v_id"])),
            up_id=("" if "up_id" not in series.index.tolist() else str(series["up_id"])),
            up_name=("" if "up_name" not in series.index.tolist() else str(series["up_name"])),
            face=("" if "face" not in series.index.tolist() else str(series["face"])),
            cover=("" if "cover" not in series.index.tolist() else str(series["cover"])),
            title=("" if "title" not in series.index.tolist() else str(series["title"])),
        )

    def update_all(self, v_id, up_id, title, up_name, face="", cover=""):
        if self._up_id:
            self.im.REMOVE(self)  # 每一次更新都要重新添加到同步管理器
        self._v_id = v_id  # 如果为None
        self._up_id = up_id
        self._up_name = up_name
        if self._up_id:
            self.im.ADD(self)
        if title:
            self.label_title.setText(title)
            self.label_title.setToolTip(title)
        if up_name:
            self.cb_upselect.setText(self._up_name)
            self.cb_upselect.setToolTip(self._up_name)
        if not face:
            df = get_up_info(self.db, up_id)
            if df.shape[0]:
                face = df["face"][0]
        if face:
            register_webImg(self.up_face, face)
        if not cover:
            df = get_video_info(self.db, v_id)
            if df.shape[0]:
                cover = df["cover"][0]
        if cover:
            register_webImg(self.v_cover, cover)
        self.update_up_tags()
        self.update_video_tags()
        self.update_up_collection()

    def set_fold_name(self, fold_name):
        self._fold_name = fold_name

    def update_up_tags(self, select: list = [], unselect: list = []):
        if not select:
            select = get_up_selectedtags(self.db, self._up_id)
        if not unselect:
            unselect = get_up_unselectedtags(self.db, self._up_id)
        self.up_select = select
        self.up_unselect = unselect
        self.cb_add_up.clear()
        self.cb_add_up.addItems(self.up_unselect)
        self.cb_del_up.clear()
        self.cb_del_up.addItems(self.up_select)
        # self.cb_del_up.clearEditText()
        self.cb_add_up.clearEditText()
        if not self.isBlocked:
            self.im.update_up_tags(self._up_id, select, unselect)

    def update_video_tags(self, select: list = [], unselect: list = []):
        if not select:
            select = get_video_selectedtags(self.db, self._v_id)
        if not unselect:
            unselect = get_video_unselectedtags(self.db, self._v_id)
        self.v_select = select
        self.v_unselect = unselect
        self.cb_add_v.clear()
        self.cb_add_v.addItems(self.v_unselect)
        self.cb_del_v.clear()
        self.cb_del_v.addItems(self.v_select)
        self.cb_add_v.clearEditText()

    def update_up_collection(self, state=None):
        if state is None:
            state = get_up_collection_state(self.db, self._up_id)
        self.isBlocked = True
        self.cb_upselect.setCheckState(state)
        self.isBlocked = False

    def on_click_toolbut(self):
        self.s_toolbar.emit(self)

    @singleton
    class InfoWidgetManager:
        up_id_table: dict[str, list[InfoWidget]] = {}

        def ADD(self, w: InfoWidget):
            if w._up_id and w._up_id in self.up_id_table.keys() and w in self.up_id_table[w._up_id]:
                return
            table = self.up_id_table.get(w._up_id, [])
            table.append(w)
            self.up_id_table[w._up_id] = table

        def REMOVE(self, w: InfoWidget):
            if w._up_id and w._up_id in self.up_id_table.keys() and w in self.up_id_table[w._up_id]:
                self.up_id_table[w._up_id].remove(w)

        def update_up_tags(self, up_id: str, select: list, unselect: list):
            table = self.up_id_table.get(up_id, [])
            for i in range(len(table) - 1, -1, -1):
                w: InfoWidget = table[i]
                if w.isDeleted:
                    table.pop(i)  # TODO 注意到有两种删除的途径
                    continue
                if w._up_id != up_id:
                    continue
                w.isBlocked = True
                w.update_up_tags(select, unselect)
                w.isBlocked = False
            # print(统计总览) 查看是否正确释放

        def update_up_collection(self, up_id: str, state=None):
            if state == None:
                state = self.up_id_table.get(up_id, [])
            table = self.up_id_table.get(up_id, [])
            for i in range(len(table) - 1, -1, -1):
                w: InfoWidget = table[i]
                if w.isDeleted:
                    table.pop(i)
                    continue
                if w._up_id != up_id:
                    continue
                w.isBlocked = True
                w.update_up_collection(state)
                w.isBlocked = False

    im: InfoWidgetManager = InfoWidgetManager()
