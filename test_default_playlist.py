"""
登录b站并扫描默认收藏夹
"""

import unittest
import sys
import traceback
from Common.Process import *
from Common.Logger import *
from Common.Abspath import *
from Web.MyWebDriver import *
from Web.biliAccess import goto_default_collectfolder
from DataAccess.DataBase import *
from DataAccess.sql_query import *
from PyQt6.QtWidgets import QApplication
from Widget.EntryWidget import EntryWidget
from Widget.PlayListWidget import PlayListWidget


class TestRunWithoutError(unittest.TestCase):
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

        cls.pm = ProcessManager()
        cls.pm.StartWorkers(3)

        cls.l = Logger()
        cls.l.info(logStart())

        cls.wd = MyWebDriver()
        cls.wd.Login()

        cls.db = DataBase()
        cls.db.Connect(videowatcher_sql_fp)
        create_all(cls.db, videowatcher_sqls)

    @classmethod
    def tearDownClass(cls):
        """整个测试类执行后调用一次"""
        print("清理测试类")
        cls.app.processEvents()

        cls.pm.__del__()
        cls.l.info(logEnd())
        cls.db.Disconnect()
        cls.wd.Quit()

    def test_biliplaylist_uncollect(self):
        try:
            print("后台取消前n个默认收藏夹中up已被选择的视频")
            w = PlayListWidget()
            w.show()
            goto_default_collectfolder(self.wd)
            w.but_current.click()
            w.pushButton.click()
            w.close()
            self.app.processEvents()  #
        except Exception:
            self.fail(
                f"test_default_playlist_uncollect 执行异常:\n{traceback.format_exc()}"
            )


class Test_function(unittest.TestCase):
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

        cls.pm = ProcessManager()
        cls.pm.StartWorkers(3)

        cls.l = Logger()
        cls.l.info(logStart())

        cls.wd = MyWebDriver()
        cls.wd.Login()

        cls.db = DataBase()
        cls.db.Connect(videowatcher_sql_fp)
        create_all(cls.db, videowatcher_sqls)

    @classmethod
    def tearDownClass(cls):
        """整个测试类执行后调用一次"""
        print("清理测试类")
        cls.app.processEvents()

        cls.pm.__del__()
        cls.l.info(logEnd())
        cls.db.Disconnect()
        cls.wd.Quit()

    def test_playlist_num(self):
        """测试读取指定数量的视频信息"""
        n = 325
        w = PlayListWidget()
        w.show()
        goto_default_collectfolder(self.wd)
        w.spinBox.setValue(n)
        w.but_current.click()
        self.app.processEvents()
        self.assertEqual(w.flow_layout.count(), n)


if __name__ == "__main__":
    unittest.main(verbosity=2)
