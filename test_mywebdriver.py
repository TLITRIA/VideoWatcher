"""
class MyWebDriver 功能测试
"""

import unittest
import sys
import traceback

from Web.MyWebDriver import *
from Web.biliAccess import download_video
from Common.Abspath import default_bili_cookietxt


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
        cls.wd = MyWebDriver()

    @classmethod
    def tearDownClass(cls):
        """整个测试类执行后调用一次"""
        print("清理测试类")
        cls.wd.Quit()

    def test_cookie_biliLogin(self):
        """检查用于登录b站的cookie是否有效"""
        url = "https://www.bilibili.com/"
        cookie_fp = default_bili_cookie
        domains = [".bilibili.com"]
        func = None
        args = None
        self.wd.Goto(url)
        if os.path.exists(cookie_fp):
            data = readjson(cookie_fp)
            for kv in data:
                if domains and kv["domain"] not in domains:
                    continue
                self.wd._driver.add_cookie(kv)
            print(f"已读取{len(data)}行cookie：{cookie_fp}")
            self.wd._driver.refresh()
        self.assertTrue(self.wd.ifLoginBilibili())

    @unittest.skip('把download文件夹全删了')
    def test_download_bilibili(self):
        """检查下载功能"""
        result = download_video(
            "BV1nwauzREuU", R"D:\__Downloads__\cache", default_bili_cookie_ytdlp
        )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
