import os, sys
from os.path import abspath, dirname

msedge_driver_path = R"F:\Env\edgedriver_win64\msedgedriver.exe"
edge_profile_path = Rf"C:/Users/{os.getlogin()}/AppData/Local/Microsoft/Edge/User Data/Default"
test_db_fp = R"E:\VideoWatcher_bk\now\db\videowatcher.db"

# default abspath
default_log_fp = abspath("./.cache/log/tmp.log")
default_bili_cookie = abspath(R"./.cookie/bilibili.json")
default_bili_cookietxt = abspath(R"./.cookie/bilibili.txt")
default_bili_cookie_ytdlp = abspath(R"./.cookie/ytdlp.txt")
default_db_fp = abspath(R"./.cache/db/videowatcher.db")
