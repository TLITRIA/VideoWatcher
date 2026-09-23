import unittest
import sys
import traceback
from pprint import pprint
from DataAccess.DataBase import *
from DataAccess.sql_query import *
from Common.Logger import *


class TestRunWithoutError(unittest.TestCase):
    """测试数据库功能，本例中使用已有的数据库文件"""

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
        cls.db = DataBase()
        cls.db.Connect("D:/__Downloads__/videowatcher.db")

    @classmethod
    def tearDownClass(cls):
        """整个测试类执行后调用一次"""
        print("清理测试类")
        cls.db.Disconnect()

    def test_db_read(self):
        with timeblock("数据库操作"):
            print("-" * 80)
            print("获取up表中数据残缺的up_id")
            pprint(get_up_unfilled(self.db))
        with timeblock("数据库操作"):
            print("-" * 80)
            print("获取up表中所有的up_id")
            pprint(get_all_up_id(self.db))
        with timeblock("数据库操作"):
            print("-" * 80)
            print("获取up表中所有的信息，以dataframe形式返回")
            print(get_all_up_df(self.db))
        with timeblock("数据库操作"):
            print("-" * 80)
            print("获取up_exclude表中所有标记排除的up的信息，以df形式返回")
            print(get_all_up_exclude_df(self.db))
        with timeblock("数据库操作"):
            print("-" * 80)
            print("获取video表中所有有tag标记的video的信息，以df形式返回")
            print(get_all_taged_video_df(self.db))
        with timeblock("数据库操作"):
            print("-" * 80)
            print("获取up表中缺少最新video的up的up_id")
            pprint(get_up_id_whichvideoisnotnew(self.db))


