'''
测试数据库编辑器
'''
import os, sys
from Widget.DbWidget import *
from Web.MyWebDriver import *
from DataAccess.DataBase import *
from DataAccess.sql_query import *
from PyQt6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    wd = MyWebDriver()
    wd.Login()

    db = DataBase()
    db.Connect(videowatcher_sql_fp)
    create_all(db, videowatcher_sqls)

    w = DbWidget()
    w.show()
    
    sys.exit(app.exec())
