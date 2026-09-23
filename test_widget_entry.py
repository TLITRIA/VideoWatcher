import unittest
import sys
import traceback
from Widget.EntryWidget import *
from PyQt6.QtWidgets import QApplication
from Web.MyWebDriver import *
from Web.biliAccess import *
from DataAccess.DataBase import *
from DataAccess.sql_query import *
from Common.Logger import *

class TestRunWithoutError(unittest.TestCase):
    """测试entryWidget"""

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
        cls.wd.selenium_options.append('--force-dark-mode')
        cls.wd.selenium_options.append('--mute-audio')
        cls.wd.Login()
        cls.db = DataBase()
        cls.db.Connect()
        create_all(cls.db, videowatcher_sqls)

    @classmethod
    def tearDownClass(cls):
        """整个测试类执行后调用一次"""
        print("清理测试类")
        cls.app.processEvents()
        cls.db.Disconnect()
        cls.wd.Quit()

    def test_parse_all_kinds_of_url(self):
        """测试entry是否正确解析webdriver url"""
        w = EntryWidget()
        w.show()
        with timeblock():
            """bilibili 视频播放页"""
            self.wd.Goto("https://www.bilibili.com/video/BV15cuV6pEnY/?spm_id_from=333.1007.tianma.1-1-1.click&vd_source=eb37b7b47eaa888d1299c60038fb6205")
            w.focus() # 或者点击按钮
        with timeblock():
            """bilibili up主视频发布页"""
            self.wd.Goto("https://space.bilibili.com/583393248/upload/video")
            w.focus()
        with timeblock():
            """bilibili 播放列表页"""
            goto_default_collectfolder(self.wd)
            w.focus()
        self.app.processEvents()

        

if __name__ == "__main__":
    unittest.main(verbosity=2)