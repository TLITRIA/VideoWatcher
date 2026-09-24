import sys
import traceback
from Common.Process import *
from Common.Logger import *
from Common.Abspath import *
from Web.MyWebDriver import *
from DataAccess.DataBase import *
from DataAccess.sql_query import *
from PyQt6.QtWidgets import QApplication
from Widget.EntryWidget import EntryWidget

if __name__ == "__main__":

    app = QApplication(sys.argv)

    pm = ProcessManager()
    pm.StartWorkers(3)

    l = Logger()
    l.info(logStart())

    wd = MyWebDriver()
    wd.Login()

    db = DataBase()
    # db.Connect(videowatcher_sql_fp)
    db.Connect("D:/__Downloads__/videowatcher.db")
    create_all(db, default_create_sqls)

    entry = EntryWidget()
    entry.show()
    # entry.pushButton_6.click() # 默认收藏夹
    entry.pushButton_4.click()  # 所有Up重新读取

    app.exec()
    pm.__del__()
    l.info(logEnd())
    wd.Quit()
    db.Disconnect()
