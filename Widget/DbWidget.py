from UI.dbViewForm import Ui_Form
import pandas as pd
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QTableWidget
from PyQt6.QtGui import QIcon, QCursor, QKeySequence, QShortcut
from PyQt6.QtCore import pyqtSignal, Qt, QStringListModel

from Web.MyWebDriver import *
from Common.FlowLayout import FlowLayout
from Common.PyQt import *
from Common.match_bili import *
from DataAccess.sql_bilibili import *
from Widget.InfoWidget import InfoWidget


class DbWidget(QWidget, Ui_Form):
    db = DataBase()
    wd = MyWebDriver()
    __tablewidget: QTableWidget
    flow_layout: FlowLayout
    s_clear_flowlayout = pyqtSignal()
    s_goto_upspace = pyqtSignal(str)  # 跳转up主页

    def on_click_bili_taged_video(self):
        self.FlowlayoutClear()
        # df = get_all_taged_video_df(self.db)
        # self.AddInfoWidgets(df)

    def on_click_bili_up_exclude(self):
        self.FlowlayoutClear()
        self.update_playlist_number()
        # 打开另一个控件
        self.__tablewidget = QTableWidget()
        self.__tablewidget.show()
        df = get_whole_table(self.db, "up_exclude")

        # 将所有的数据添加到表格中
        self.__tablewidget.setRowCount(len(df))
        self.__tablewidget.setColumnCount(len(df.columns))
        for i in range(len(df)):
            for j in range(len(df.columns)):
                self.__tablewidget.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))
        # 设置表头
        self.__tablewidget.setHorizontalHeaderLabels(df.columns)
        # 设置指定列可以编辑
        self.__tablewidget.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)

        # 捕获指定标签的修改
        def update_one_reason(item: QTableWidgetItem):
            if item == None:
                return
            hitem = self.__tablewidget.horizontalHeaderItem(item.column())
            if hitem == None or hitem.text() != "reason":
                return
            ret = []
            col = []
            ret.append(str(self.__tablewidget.item(item.row(), 0).text()))  # TODO Magic number 0
            col.append("up_id")
            ret.append(str(item.text()))
            col.append("reason")
            df = pd.DataFrame([ret], columns=col)
            insert_up(self.db, df, "up_exclude")

        self.__tablewidget.itemChanged.connect(lambda item: update_one_reason(item))

        # 捕获单元格点击
        def on_cell_click(row: int, col: int):
            item = self.__tablewidget.item(row, col)
            if item == None:
                return
            hitem = self.__tablewidget.horizontalHeaderItem(col)
            if hitem == None or hitem.text() != "url":
                return
            # self.s_goto_upspace.emit(str(item.text()))
            self.wd.Goto(str(item.text()))

        self.__tablewidget.cellClicked.connect(lambda row, col: on_cell_click(row, col))

        # 捕获单元格删除
        def on_cell_delete(self):
            row = self.__tablewidget.currentRow()
            col = self.__tablewidget.currentColumn()
            item = self.__tablewidget.item(row, col)
            if item == None:
                return
            up_id = str(match_upspace(item.text()))
            print(f"删除up_id: {up_id}")
            delete_up(self.db, up_id, "up_exclude")
            self.__tablewidget.removeRow(row)
        ks_del = QShortcut(QKeySequence("Delete"), self.__tablewidget)
        ks_del.setContext(Qt.ShortcutContext.WidgetShortcut)
        ks_del.activated.connect(lambda: on_cell_delete(self))

        self.__tablewidget.resize(800, 600)

    def on_click_bili_up(self):
        self.FlowlayoutClear()
        self.AddInfoWidgets(get_whole_table(self.db, "up"))

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
            w.s_goto_videopage.connect(lambda url: self.wd.Goto(url) if url else None)
            w.s_goto_upspace.connect(lambda url: self.wd.Goto(url) if url else None)
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

    def update_playlist_number(self, n: int | None = None):
        if n is None:
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
    db.Connect()
    create_all(db, default_create_sqls)

    w = DbWidget()
    w.show()
    w.but_bili_up_exc.click()

    sys.exit(app.exec())
    db.Disconnect()
    wd.Quit()
