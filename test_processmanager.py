"""ProcessManager功能测试"""

import unittest
import sys
import traceback
from Common.Process import *

from DataAccess.DataBase import *
from DataAccess.sql_query import *
import pandas as pd


class Test_1(unittest.TestCase):
    def setUp(self):
        """每个测试方法执行前调用"""
        print("初始化测试方法")

    def tearDown(self):
        """每个测试方法执行后调用"""
        print("清理测试方法")

    @classmethod
    def setUpClass(cls):
        """整个测试类执行前调用一次"""
        print("初始化测试类")
        cls.pm = ProcessManager()
        cls.pm.StartWorkers(3)
        cls.db = DataBase()
        cls.db.Connect("D:/__Downloads__/videowatcher.db")

    @classmethod
    def tearDownClass(cls):
        """整个测试类执行后调用一次"""
        print("清理测试类")
        cls.pm.__del__()
        cls.db.Disconnect()
