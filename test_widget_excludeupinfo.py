import unittest
import sys
import traceback
from PyQt6.QtWidgets import QApplication
from Web.MyWebDriver import *
from Web.biliAccess import *
from DataAccess.DataBase import *
from DataAccess.sql_bilibili import *
from Common.Logger import *


class TestRunWithoutError(unittest.TestCase):
    """测试"""

    def setUp(self):
        """每个测试方法执行前调用"""
        print("每个测试方法执行前调用")

    def tearDown(self):
        """每个测试方法执行后调用"""
        print("每个测试方法执行后调用")

    @classmethod
    def setUpClass(cls):
        """整个测试类执行前调用一次"""
        print("初始化测试类")
        cls.app = QApplication(sys.argv)
        cls.wd = MyWebDriver()
        cls.wd.selenium_options.append("--force-dark-mode")
        cls.wd.selenium_options.append("--mute-audio")
        cls.wd.Login()
        cls.db = DataBase()
        cls.db.Connect()
        create_all(cls.db, default_create_sqls)

    @classmethod
    def tearDownClass(cls):
        """整个测试类执行后调用一次"""
        print("清理测试类")
        cls.app.processEvents()
        cls.db.Disconnect()
        cls.wd.Quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
