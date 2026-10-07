import subprocess
from Web.MyWebDriver import *


def ytb_scroll_to_bottom(wd: MyWebDriver):
    last_count = 0
    while last_count != len(wd.xpath_wait("//ytd-rich-item-renderer")):
        wd.xpath_wait("//a[@class='ytLockupViewModelContentImage']")
        last_count = len(wd.xpath_findall("//ytd-rich-item-renderer"))
        body = wd._driver.find_element(By.TAG_NAME, "body")
        for _ in range(2):
            body.send_keys(Keys.END)
        time.sleep(4)


def ytb_download_video(
    vid, downfold, limit_rate: int = 0, possible_title: str = "", cookie: str = default_ytb_cookie_ytdlp
) -> subprocess.CompletedProcess:
    if os.path.exists(downfold):
        if scan_foldsize(downfold) > 0:  # TODO 判断已下载的逻辑，需要更进一步的验证
            print(f"文件夹 {downfold} 已存在且不为空，跳过下载")
            return subprocess.CompletedProcess(args=[], returncode=0)
    else:
        g_mkdir_byfp(downfold)

    cmd = ["yt-dlp"]  # TODO .conf
    cmd.extend(["-vU"])  # 调试信息
    # cmd.extend(["--impersonate", "chrome"])  # curl_cffi
    # cmd.extend(["--socket-timeout", "60"])
    # cmd.extend(["-f", "bestvideo+bestaudio"])
    cmd.extend(["-o", f"{downfold}%(title)s.%(ext)s"])
    cmd.extend(["--no-playlist"])
    cmd.extend(["--limit-rate", f"{limit_rate}M"] if limit_rate > 0 else [])
    # cmd.extend(["--merge-output-format", "mp4"])
    cmd.extend(["--extractor-args", 'youtube:player_client=tv,mweb'])
    cmd.extend(["--cookies", cookie] if cookie != "" else [])
    cmd.append("-i")
    cmd.extend(["--write-subs", "--write-auto-subs"])
    cmd.extend(["--sub-langs", "en,zh-Hans,ai-zh,ai-en"])
    cmd.extend(["--convert-subs", "srt"])
    cmd.extend(["-o", f"subtitle:{downfold}%(title)s.%(ext)s"])
    cmd.append(f"https://www.youtube.com/watch?v={vid}")
    print(cmd)
    result = subprocess.run(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr, text=True)
    time.sleep(5)
    return result


def ifLoginYouTube(wd: MyWebDriver):
    return bool(wd.xpath_wait("//div/span[contains(text(), '登录')]") == [])


def ytb_login(wd: MyWebDriver):
    if not wd._isQuit:
        wd.Quit()
    wd.Login(
        url="https://www.youtube.com/",
        cookie_fp=default_ytb_cookie,
        cookietxt_fp=default_ytb_cookietxt,
        cookie_ytdlp_fp=default_ytb_cookie_ytdlp,
        domains=[".youtube.com"],
        func=ifLoginYouTube,
        args=[wd],
    )


if __name__ == "__main__":
    ytb_login(MyWebDriver())
    ytb_download_video("mNhqm6bKUf0", abspath(R"./.cache/downloadtest/") + "/")
    pass
