
from Web.MyWebDriver import *

def ytb_scroll_to_bottom(wd:MyWebDriver):
    last_count = 0
    while last_count != len(wd.xpath_wait("//ytd-rich-item-renderer")):
        wd.xpath_wait("//a[@class='ytLockupViewModelContentImage']")
        last_count = len(wd.xpath_findall("//ytd-rich-item-renderer"))
        body = wd._driver.find_element(By.TAG_NAME, "body")
        for _ in range(2):
            body.send_keys(Keys.END)
        time.sleep(4)