from os.path import abspath
from typing import Callable
import pandas
from pprint import pprint
from netscape_cookies.netscape_cookies import save_cookies_to_file

from selenium.webdriver import Edge
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService


from Common.Convert import *
from Common.Logger import *
from Common.Common import *
from Common.Abspath import *
from Pattern.singleton import singleton
from Web.MyWebDriver import *


@singleton
class MyWebDriver:
    def __init__(self):
        self._chorme = "edge"
        self._isQuit = True
        self.selenium_options = [
            "--disable-blink-features=AutomationControlled",
            "log-level=3",
            "--edge-skip-compat-layer-relaunch",
            "--no-first-run",
            # "--disk-cache-size=0", # 禁止磁盘缓存，强制使用内存缓存
            # "--disable-crash-reporter", # 禁用崩溃报告
            # "--user-data-dir=E:/Cache/Selenium", # 用户数据重定向
            # '--window-size=1920,1080',
            "--ignore-certificate-errors",  # 忽略证书错误
            "--start-maximized",  # 启动时最大化
        ]

    def __del__(self):
        if not self._isQuit:
            self.Quit()

    def _generate_driver(self):
        self._option = EdgeOptions()
        self._option.add_experimental_option("useAutomationExtension", False)
        self._option.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
        )
        for option in self.selenium_options:
            try:
                self._option.add_argument(option)
            except Exception as e:
                print(e)
        self._service = EdgeService(msedge_driver_path)
        self._driver = Edge(self._option, self._service)
        self._driver_wait = WebDriverWait(self._driver, 7)
        self._driver.implicitly_wait(2)
        self._isQuit = False

    def Quit(self):
        if not self._isQuit:
            self._driver.quit()
            self._isQuit = True

    def Goto(self, url: str):
        if self._isQuit:
            self._generate_driver()
        # self.Focus()
        try:
            if self._driver.current_url != url:
                with timeblock(f"Goto({url})"):
                    self._driver.get(url)
        except WebDriverException as e:
            self._driver.get(url)
        return self._driver

    def xpath_findall(self, xp):
        return self._driver.find_elements(By.XPATH, xp)

    def xpath_pprint(self, xp):
        nodes = self.xpath_findall(xp)
        for node in nodes:
            print("-" * 80)
            pprint(node.get_attribute("textContent"))
            print("=" * 80)
        print(f"共搜索到{len(nodes)}个结果")
        return nodes

    def xpath_wait(self, xp):
        elements = []
        try:
            with timeblock(f"Wait({xp})"):
                elements = self._driver_wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, xp))
                )
        except TimeoutException:
            print(f"超时：未通过 XPath '{xp}' 找到任何元素")
        return elements

    def ClickNode(self, node: WebElement):
        text = node.get_attribute("textContent")
        if text:
            text = text.strip()
        with timeblock(f"ClickNode({text})"):
            self._driver.execute_script("arguments[0].click();", node)

    def ClickGotoNode(self, node: WebElement):
        if not node:
            raise
            return
        before_handles = self._driver.window_handles
        self.ClickNode(node)
        try:
            self._driver_wait.until(
                lambda dr: len(dr.window_handles) > len(before_handles)
            )
            new_handle = list(
                set(self._driver.window_handles) - set(before_handles)
            )[0]
            self._driver.switch_to.window(new_handle)
            print("转到新窗口")
        except:
            pass

    def ifLoginBilibili(
        self,
    ):
        return bool(
            self.xpath_findall("//div/div/span[contains(text(), '登录')]") == []
            and self.xpath_findall("//div[@class='bili-avatar']") != []
        )

    def Login(
        self,
        url="https://www.bilibili.com/",
        cookie_fp=default_bili_cookie,
        cookietxt_fp=default_bili_cookietxt,
        cookie_ytdlp_fp=default_bili_cookie_ytdlp,
        domains=[".bilibili.com"],
        func=None,
        args=None,
    ):
        self.Quit()
        hasHeadless = "--headless" in self.selenium_options
        if hasHeadless:
            self.selenium_options.remove("--headless")

        self.Goto(url)
        if os.path.exists(cookie_fp):
            data = readjson(cookie_fp)
            for kv in data:
                if domains and kv["domain"] not in domains:
                    continue
                self._driver.add_cookie(kv)
            print(f"已读取{len(data)}行cookie：{cookie_fp}")
            self._driver.refresh()

        if not func or not args:
            func = self.ifLoginBilibili
            args = []

        while not func(*args):
            input(f"请手动在 {url} 登录后按回车继续...")
            self.Goto(url)
        print(f"{url} 登录成功")

        if cookie_fp:
            if not os.path.exists(cookie_fp):
                g_mkdir_byfp(cookie_fp)
            savejson(cookie_fp, self._driver.get_cookies())
        if cookietxt_fp:
            if not os.path.exists(cookietxt_fp):
                g_mkdir_byfp(cookietxt_fp)
            save_cookies_to_file(self._driver.get_cookies(), cookietxt_fp)
            # 手动添加前缀 ： {# Netscape HTTP Cookie File}
            with open(cookietxt_fp, "r") as fr:
                content = fr.read()
                with open(cookie_ytdlp_fp, "w") as fw:
                    fw.write("# Netscape HTTP Cookie File\n" + content)

        if hasHeadless:
            self.selenium_options.append("--headless")
            self.Quit()
            self.Goto(url)

    def ScrollToBottomAndBack(self):
        if self._isQuit:
            return
        body = self._driver.find_element(By.TAG_NAME, "body")
        for _ in range(2):
            body.send_keys(Keys.END)
        time.sleep(1)
        for _ in range(2):
            body.send_keys(Keys.HOME)

    def FocusHead(self):
        """
        强制转到第一个窗口
        """
        print("转到第一个窗口")
        if (
            not self._isQuit
            and hasattr(self, "_driver")
            and len(self._driver.window_handles)
        ):
            self._driver.switch_to.window(self._driver.window_handles[0])


def xpath(node: WebElement, xp: str):
    return node.find_elements(By.XPATH, xp)


def xpath_w(node: WebElement, xp: str, timeout=2):
    wait = WebDriverWait(node.parent, timeout)
    return wait.until(lambda _: node.find_elements(By.XPATH, xp))


def node_pprint(nodes: list[WebElement]):
    for node in nodes:
        print("-" * 80)
        pprint(node.get_attribute("textContent"))
        print("=" * 80)
    print(f"共{len(nodes)}个结果")


def scroll_to_bottommost(
    wd: MyWebDriver, xp: str, interval=7, maxrets=200, func=None, args=None
):
    last_count = 0
    while last_count != len(wd.xpath_wait(xp)):  # 1 滚动到最低点 即退出
        last_count = len(wd.xpath_findall(xp))
        if func and args:
            if func(*args):
                break  # 2 满足func 即退出
        if last_count > maxrets:
            break  # 3 获取到足够多的结果 即退出
        body = wd._driver.find_element(By.TAG_NAME, "body")
        for _ in range(2):
            body.send_keys(Keys.END)
            time.sleep(1)
        time.sleep(interval)


def turning_page(
    wd: MyWebDriver,
    start_url: str,
    f_getinfo: Callable[[MyWebDriver]],
    f_getnextbut: Callable[[MyWebDriver],],
    f_concat: Callable[[pandas.DataFrame, pandas.DataFrame], pandas.DataFrame],
    f_interse: Callable[[pandas.DataFrame, pandas.DataFrame], bool],
    maxrets: int = -1,  # 默认全部读取
) -> pandas.DataFrame:
    results = pandas.DataFrame()
    if wd._driver.current_url != start_url:
        wd.Goto(start_url)
    while True:
        tmp_ret = f_getinfo(wd)
        if f_interse(tmp_ret, results):
            results = f_concat(results, tmp_ret)  # 防止遗漏
            break  # 当翻页前后结果一致时退出
        results = f_concat(results, tmp_ret)
        if maxrets >= 0 and results.shape[0] >= maxrets:
            break  # 当获取足够的结果后退出
        try:
            wd.ClickNode(f_getnextbut(wd)[0])
        except:
            break
        time.sleep(2)
    # 如果df数目超出，截取前n项
    if results.shape[0] > maxrets:
        results = results.iloc[:maxrets]
    return results


if __name__ == "__main__":
    wd = MyWebDriver()
    wd.Login()
