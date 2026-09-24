from UI.excludeUpInfoForm import Ui_Form
import os, sys
import pandas as pd

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, Qt

from DataAccess.DataBase import *
from DataAccess.sql_query import *
from Common.PyQt import register_webImg


class ExcludeUpInfoWidget(QWidget, Ui_Form):
    isDeleted: bool
    isBlocked: bool
    _up_id: str
    db: DataBase
    s_goto_upspace = pyqtSignal(str)  # 跳转up主页
    s_mydel = pyqtSignal(QWidget)  #

    def on_up_tristate(self, state: Qt.CheckState):
        if self.isBlocked or self.isDeleted:
            return
        if self.db.isConnected and self._up_id:
            update_one_up_exclude(
                self.db,
                self._up_id,
                self.plainTextEdit.toPlainText(),
                state == Qt.CheckState.Checked,
                f"https://space.bilibili.com/{self._up_id}/upload/video",
            )
            if state == Qt.CheckState.PartiallyChecked:
                insert_up_null(self.db, self._up_id)
            else:
                delete_up(self.db, self._up_id)

    def on_plainText_changed(self):
        if self.isBlocked or self.isDeleted:
            return
        if self.db.isConnected and self._up_id:
            update_one_up_exclude(
                self.db,
                self._up_id,
                self.plainTextEdit.toPlainText(),
                self.cb_upselect.checkState() == Qt.CheckState.Checked,
                f"https://space.bilibili.com/{self._up_id}/upload/video",
            )

    def __init__(self, parent=None):
        super(ExcludeUpInfoWidget, self).__init__(parent)
        self.setupUi(self)
        self.isDeleted = False  # 自己管理是否被丢弃
        self.isBlocked = False  # 操作是否屏蔽
        self.db = DataBase()
        self.but_gospace.clicked.connect(
            lambda _: (
                self.s_goto_upspace.emit(f"https://space.bilibili.com/{self._up_id}/upload/video")
                if self._up_id is not None
                else None
            )
        )
        # self.but_gospace_2.clicked.connect(lambda _: self.s_mydel.emit())

    def MyDel(self):
        self.isDeleted = True

    def series_update_all(self, series: pd.Series):
        s_taglist = series.index.tolist()
        for tag in ["up_id", "reason", "yes_no"]:
            if tag not in s_taglist:
                return False

        self._up_id = str(series["up_id"])

        self.isBlocked = True
        self.plainTextEdit.setPlainText(str(series["reason"]))
        state = Qt.CheckState.Checked if int(series["yes_no"]) == 1 else Qt.CheckState.PartiallyChecked
        self.cb_upselect.setCheckState(state)
        self.isBlocked = False

        # 从up表中读取数据
        updf = get_up_info(self.db, self._up_id)
        if len(updf) != 1:
            self.cb_upselect.setText(self._up_id)
            self.up_face.setText("None")
        else:
            up_series = updf.iloc[0]
            if "up_name" in up_series.index.tolist():
                self.cb_upselect.setText(str(up_series["up_name"]))
            if "face" in up_series.index.tolist():
                if str(up_series["face"]) != "":
                    register_webImg(self.up_face, str(up_series["face"]))


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    from Web.MyWebDriver import *

    app = QApplication(sys.argv)
    wd = MyWebDriver()
    wd.selenium_options.append("--force-dark-mode")
    wd.selenium_options.append("--mute-audio")
    wd.Login()
    db = DataBase()
    db.Connect("D:/__Downloads__/videowatcher.db")
    create_all(db, default_create_sqls)

    w = ExcludeUpInfoWidget()
    w.but_gospace.clicked.connect(
        lambda _: (wd.Goto(f"https://space.bilibili.com/{w._up_id}/upload/video") if w._up_id is not None else None)
    )
    w.show()
    df = get_all_up_exclude_df(db)
    print(type(df.iloc[0]))
    w.series_update_all(df.iloc[0])

    sys.exit(app.exec())
    db.Disconnect()
    wd.Quit()
