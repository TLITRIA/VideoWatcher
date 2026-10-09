from UI.editUptagsForm import Ui_Form
import os, sys
import pandas as pd
import numpy as np
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QTableWidget
from PyQt6.QtGui import QIcon, QCursor, QKeySequence, QShortcut
from PyQt6.QtCore import pyqtSignal, Qt, QStringListModel
from DataAccess.DataBase import DataBase
from DataAccess.sql_bilibili import *
from Web.MyWebDriver import MyWebDriver
from Common.PyQt import *


def parse_tags(string: str) -> set[str]:
    return set([x for x in (s.strip() for s in string.split(";")) if x])


def generate_tagstring(tags: set[str]) -> str:
    return "; ".join(sorted(tags))


class EditUptagsWidget(QWidget, Ui_Form):
    __db: DataBase
    __uptable: str
    __updf: pd.DataFrame
    __uptagtable: str
    __uptagdf: pd.DataFrame
    __wd: MyWebDriver
    __tags: set[str]  # 所有标签
    __tags_selected: set[str]  # 已选标签
    __tags_unselected: set[str]  # 反选标签

    def set_tablewidget_connections(self):
        """有关tablewidget的连接函数，只允许在初始化时调用"""

        def on_cell_click_goto(row: int, col: int):
            item = self.tableWidget.item(row, col)
            if item == None:
                return
            hitem = self.tableWidget.horizontalHeaderItem(col)
            if hitem == None or hitem.text() != "url":
                return
            self.__wd.Goto(item.text())

        self.tableWidget.cellClicked.connect(on_cell_click_goto)

        def on_cell_delete():
            item = self.tableWidget.currentItem()
            if item == None:
                return
            row = self.tableWidget.currentRow()
            self.tableWidget.removeRow(row)
            self.update_bottom_label()

        shortcut_del = QShortcut(QKeySequence("Delete"), self.tableWidget)
        shortcut_del.setContext(Qt.ShortcutContext.WidgetShortcut)
        shortcut_del.activated.connect(on_cell_delete)

    def on_add_select(self, i: int):
        """添加选择"""
        print(f"on_add_select({i}):{self.comboBox_tags_selected.itemText(i)}")
        self.__tags_selected.add(self.comboBox_tags_selected.itemText(i))
        self.update_tags()

    def on_add_unselect(self, i: int):
        """添加反选"""
        print(f"on_add_unselect({i}):{self.comboBox_tags_unselected.itemText(i)}")
        self.__tags_unselected.add(self.comboBox_tags_unselected.itemText(i))
        self.update_tags()

    def on_lineedit_textchange(self, string: str):
        if self.isblock != 0:
            return
        print(f"on_combo_textchange()")
        self.__tags_selected = parse_tags(self.lineEdit_tags_selected.text())
        self.__tags_unselected = parse_tags(self.lineEdit_tags_unselected.text())
        self.update_tags()

    def on_change_oneup_tags(self, item: QTableWidgetItem):
        if self.isblock != 0:
            return
        iditem = self.tableWidget.item(item.row(), self.columns.index("up_id"))
        if iditem is None:
            return
        tags = parse_tags(item.text())
        rebuild_up_tags(self.__db, iditem.text(), list(tags))
        self.isblock += 1
        item.setText(generate_tagstring(tags))
        self.__uptagdf = get_whole_table(self.__db, self.__uptagtable)
        self.isblock -= 1

    def __init__(self, parent=None):
        super(EditUptagsWidget, self).__init__(parent)
        self.setupUi(self)
        self.__db = DataBase()
        if not self.__db.isConnected:
            self.__db.Connect()
        self.__wd = MyWebDriver()
        self.__tags_selected = set()
        self.__tags_unselected = set()
        self.__uptable = ""
        self.__uptagtable = ""
        self.columns = ["up_id", "up_name", "up_sum", "url", "taglist"]  # 修改列名只要修改这里
        self.isblock = 0

        self.tableWidget.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked | QTableWidget.EditTrigger.EditKeyPressed
        )
        self.tableWidget.setSortingEnabled(True)
        self.setWindowTitle("编辑UP主标签")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowCloseButtonHint)

        self.wheelblocker = WheelBlocker(self)
        self.comboBox_tags_selected.installEventFilter(self.wheelblocker)
        self.comboBox_tags_unselected.installEventFilter(self.wheelblocker)

        self.set_tablewidget_connections()
        shortcut_f5 = QShortcut(QKeySequence("F5"), self)
        shortcut_f5.activated.connect(lambda: self.reload_data(self.__uptable, self.__uptagtable))

    def reload_data(self, uptable: str, uptagtable: str):
        """重新读取数据并更新整个控件"""
        if not uptable or uptable == "" or not uptagtable or uptagtable == "":
            return
        self.__uptable = uptable
        self.__updf = get_whole_table(self.__db, self.__uptable)
        self.__uptagtable = uptagtable
        self.__uptagdf = get_whole_table(self.__db, self.__uptagtable)

        self.reload_tags()
        self.update_bottom_label()

    def update_bottom_label(self, text: str = ""):
        if text and text != "":
            self.label_bottom.setText(text)
        else:
            self.label_bottom.setText(f"{self.tableWidget.rowCount()} 行，{self.tableWidget.columnCount()} 列")

    def reload_tags(self):
        """重新加载标签，并清空选中状态"""
        if self.__uptagdf is None or self.__uptagdf.empty:
            return  # 通过检查条件反应这一函数与哪些变量有关
        self.__tags_selected = set()
        self.__tags_unselected = set()
        self.__tags = set(self.__uptagdf["tag"].tolist())
        self.isblock += 1
        self.comboBox_tags_unselected.clear()
        self.comboBox_tags_selected.clear()
        self.isblock -= 1
        self.update_tags()

    def update_tags(self):
        """根据所有标签、已选标签、反选标签更新tablewidget"""
        print("update_tags")
        print(self.__tags_selected)
        print(self.__tags_unselected)
        extra_tags = sorted(list(self.__tags - self.__tags_selected - self.__tags_unselected))
        self.isblock += 1
        self.lineEdit_tags_selected.setText(generate_tagstring(self.__tags_selected))
        self.lineEdit_tags_unselected.setText(generate_tagstring(self.__tags_unselected))
        self.comboBox_tags_unselected.clear()
        self.comboBox_tags_unselected.addItems(extra_tags)
        self.comboBox_tags_selected.clear()
        self.comboBox_tags_selected.addItems(extra_tags)
        self.isblock -= 1

        # 根据选中状态更新tablewidget，先全部读取，再逐行删除
        self.update_tablewidget()
        index_taglist = self.columns.index("taglist")
        for i in reversed(range(self.tableWidget.rowCount())):
            item = self.tableWidget.item(i, index_taglist)
            if item is None:
                continue
            tagset = parse_tags(item.text())
            if tagset & self.__tags_unselected:  # tagset 包含任意的反选项
                self.tableWidget.removeRow(i)
            elif tagset & self.__tags_selected != self.__tags_selected:
                self.tableWidget.removeRow(i)  # 已选项任意一项不在taglist中
        self.update_bottom_label()

    def update_tablewidget(self):
        """更新整个表格"""
        if self.__updf is None or self.__updf.empty or self.__uptagdf is None or self.__uptagdf.empty:
            return
        self.tableWidget.clearContents()
        # 直接写入的列
        self.tableWidget.setRowCount(self.__updf.shape[0])
        self.tableWidget.setColumnCount(len(self.columns))
        self.tableWidget.setHorizontalHeaderLabels(self.columns)
        updf_columns = self.__updf.columns.tolist()
        self.tableWidget.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked | QTableWidget.EditTrigger.EditKeyPressed
        )
        self.isblock += 1
        for i in range(self.__updf.shape[0]):
            for j, words in enumerate(self.columns):
                try:
                    index = updf_columns.index(words)
                    val = self.__updf.iloc[i, index]
                    if type(val) == np.int64:
                        val = int(val)
                    item = QTableWidgetItem()
                    item.setData(Qt.ItemDataRole.DisplayRole, val)
                    self.tableWidget.setItem(i, j, item)
                except Exception as e:
                    if type(e) != ValueError:
                        print(e)
                item = self.tableWidget.item(i, j)
                if item is not None:
                    if self.columns[j] == "taglist":
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                    else:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        # 要计算的列 tags TODO up 粉丝数，视频数，平均播放量，平均点赞数，平均评论数，总时长等等等等
        index_upid = self.columns.index("up_id")
        index_tags = self.columns.index("taglist")
        for i in range(self.__updf.shape[0]):
            item = self.tableWidget.item(i, index_upid)
            if item is None:
                continue
            up_id = item.text()
            tags = self.__uptagdf[self.__uptagdf["up_id"] == up_id]["tag"].tolist()
            item = QTableWidgetItem()
            item.setData(Qt.ItemDataRole.DisplayRole, generate_tagstring(set(tags)))
            self.tableWidget.setItem(i, index_tags, item)
        self.isblock -= 1


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    w = EditUptagsWidget()
    w.show()
    w.reload_data("up", "up_tag")

    sys.exit(app.exec())
