from Web.MyWebDriver import *

class BackWebDriver(MyWebDriver().__class__): # 由于装饰器闭包导致的问题
    def __init__(self):
        super().__init__()
        self.selenium_options.append('--force-dark-mode')
        self.selenium_options.append('--mute-audio')
        

    def Login(
            self,
            url="https://www.bilibili.com/",
            cookie_fp=g_bili_cookie,
            cookietxt_fp=g_bili_cookietxt,
            domains=[".bilibili.com"],
            func=None,
            args=None,
        ):
            self.Quit()
            self.Goto(url)
            self._driver.minimize_window() # 最小化窗口
            if os.path.exists(cookie_fp):
                data = readjson(cookie_fp)
                for kv in data:
                    if domains and kv["domain"] not in domains:
                        continue
                    self._driver.add_cookie(kv)
                print(f"已读取{len(data)}行cookie：{cookie_fp}")
                self._driver.refresh()
    
            def ifLoginBilibili(wd: MyWebDriver, xp):
                return bool(wd.xpath_findall(xp) == [])
    
            if not func or not args:
                func = ifLoginBilibili
                args = [self, "//div/div/span[contains(text(), '登录')]"]
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
    