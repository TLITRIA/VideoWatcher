import unittest
import sys
import traceback
from Widget.ExcludeUpInfoWidget import *
from PyQt6.QtWidgets import QApplication
from Web.MyWebDriver import *
from Web.biliAccess import *
from DataAccess.DataBase import *
from DataAccess.sql_query import *
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
        cls.db.Connect(test_db_fp)
        create_all(cls.db, default_create_sqls)

    @classmethod
    def tearDownClass(cls):
        """整个测试类执行后调用一次"""
        print("清理测试类")
        cls.app.processEvents()
        cls.db.Disconnect()
        cls.wd.Quit()

    def test_first_up_in_excludeup(self):
        """测试编辑excludeup表中第一条记录"""
        try:
            w = ExcludeUpInfoWidget()
            w.show()
            df = get_all_up_exclude_df(self.db)
            if len(df) == 0:
                return
            w.series_update_all(df.iloc[0])
            self.app.processEvents()
        except Exception:
            self.fail(f"test_first_up_in_excludeup 执行异常:\n{traceback.format_exc()}")
