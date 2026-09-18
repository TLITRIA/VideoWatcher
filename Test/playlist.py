from Widget.PlayListWidget import PlayListWidget
from PyQt6.QtWidgets import QApplication
from DataAccess.DataBase import *
from DataAccess.sql_query import *
from Web.MyWebDriver import *
from Web.BackWebDriver import *

def main():
    app = QApplication(sys.argv)
    # backD = BackWebDriver()
    # backD._generate_driver()
    # backD.Login()

    db = DataBase()
    db.Connect(videowatcher_sql_fp)
    create_all(db, videowatcher_sqls)

    wd = MyWebDriver()
    wd.Login()
    w = PlayListWidget()
    w.show()
    # w.but_default.click()

    sys.exit(app.exec())
    wd.Quit()
    db.Close()
