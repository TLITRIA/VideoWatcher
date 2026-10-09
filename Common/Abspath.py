import os, sys
from os.path import abspath, dirname

msedge_driver_path = R"F:\Env\edgedriver_win64\msedgedriver.exe"
edge_profile_path = Rf"C:/Users/{os.getlogin()}/AppData/Local/Microsoft/Edge/User Data/Default"
# test_db_fp = R"E:\VideoWatcher_bk\now\db\videowatcher.db"
# download_root = abspath("./.cache/download/")
download_root = abspath("./.download/")

# default abspath
default_log_fp = abspath("./.cache/log/tmp.log")

default_bili_cookie = abspath(R"./.cookie/bilibili.json")
default_bili_cookietxt = abspath(R"./.cookie/bilibili.txt")
default_bili_cookie_ytdlp = abspath(R"./.cookie/ytdlp_bilibili.txt")

default_ytb_cookie = abspath(R"./.cookie/youtube.json")
default_ytb_cookietxt = abspath(R"./.cookie/youtube.txt")
default_ytb_cookie_ytdlp = abspath(R"./.cookie/ytdlp_youtube.txt")
default_ytb_cookieeditor_ytdlp = abspath(R"./.cookie/ytdlp_ytb_cookie-editor.txt")

default_db_fp = abspath(R"./.cache/db/videowatcher.db")
default_csv_fold = abspath("./.cache/csv/")

# end
