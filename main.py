from os.path import abspath 
from Widget.EntryWidget import *
from PyQt6.QtWidgets import QApplication
from Common.Logger import *
from Common.Process import *
from DataAccess.DataBase import *
from DataAccess.sql_query import *
from Web.MyWebDriver import MyWebDriver

if __name__ == "__main__":
    pm = ProcessManager()
    pm.StartWorkers(3)
    
    l = Logger(abspath("./.cache/log/tmp.log"))
    l.info(logStart())
    
    wd = MyWebDriver()
    wd.Login()

    db = DataBase()
    db.Connect(videowatcher_sql_fp)
    create_all(db, videowatcher_sqls)

    app = QApplication(sys.argv)

    entry = EntryWidget()
    entry.show()

    sys.exit(app.exec())
    l.info(logEnd())
    wd.Quit()
    db.Close()
        