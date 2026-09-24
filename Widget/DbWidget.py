from UI.dbViewForm import Ui_Form
import pandas as pd
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIcon, QCursor
from PyQt6.QtCore import pyqtSignal, Qt, QStringListModel

from Web.MyWebDriver import *
from Common.FlowLayout import FlowLayout
from DataAccess.sql_query import *
from Widget.InfoWidget import InfoWidget
from Widget.ExcludeUpInfoWidget import ExcludeUpInfoWidget


class DbWidget(QWidget, Ui_Form):
    __db = DataBase()
    wd = MyWebDriver()
    flow_layout: FlowLayout
    s_clear_flowlayout = pyqtSignal()

    def on_click_bili_taged_video(self):
        self.FlowlayoutClear()
        df = get_all_taged_video_df(self.__db)
        self.AddInfoWidgets(df)

    def on_click_bili_up_exclude(self):
        self.FlowlayoutClear()
        df = get_all_up_exclude_df(self.__db)
        for i in range(len(df)):
            series = df.iloc[i]
            if int(series["yes_no"]) == 0:
                continue
            w = ExcludeUpInfoWidget(self)
            w.series_update_all(series)
            w.setFixedSize(250, 110)
            self.flow_layout.addWidget(w)
            w.s_goto_upspace.connect(lambda url: self.wd.Goto(url))
            w.s_mydel.connect(lambda w: w.MyDel() or self.removeFlowLayout(w))
        self.update_playlist_number()

    def on_click_bili_up(self):
        self.FlowlayoutClear()
        df = get_all_up_info(self.__db)
        self.AddInfoWidgets(df)

    def __init__(self, parent=None):
        super(DbWidget, self).__init__()
        self.setupUi(self)

        self.scrollArea.setWidgetResizable(True)
        container = QWidget()
        self.flow_layout = FlowLayout(container, margin=10, spacing=10)
        self.scrollArea.setWidget(container)

        self.update_playlist_number()

    def AddInfoWidgets(self, df: pd.DataFrame, dialog=None):
        for i in range(len(df)):
            # tmp_df = df.iloc[i:i+1, :]
            w = InfoWidget(self)
            w.series_update_all(df.iloc[i])
            w.setFixedSize(260, 155)
            self.flow_layout.addWidget(w)

            w.s_toolbar.connect(lambda w: print("toolbar"))
            w.s_goto_videopage.connect(
                lambda url: self.wd.Goto(url) if url else None
            )
            w.s_goto_upspace.connect(
                lambda url: self.wd.Goto(url) if url else None
            )
            w.s_del_infoW.connect(self.removeFlowLayout)
        self.update_playlist_number()

    def FlowlayoutClear(self):
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item and item.widget():
                w: InfoWidget = item.widget()
                w.isDeleted = True
                w.deleteLater()
        self.s_clear_flowlayout.emit()
        self.update_playlist_number()

    def removeFlowLayout(self, w: QWidget):
        self.flow_layout.removeWidget(w)
        w.deleteLater()
        self.update_playlist_number()

    def update_playlist_number(self):
        n = self.flow_layout.count()
        self.label.setText(f"共计 {n} 个结果")


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
    create_all(db, videowatcher_sqls)

    w = DbWidget()
    w.show()
    w.but_bili_up_exc.click()

    sys.exit(app.exec())
    db.Disconnect()
    wd.Quit()
