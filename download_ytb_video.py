import pandas as pd
from Common.Abspath import *
from Common.Process import *
from Common.Logger import *
from DataAccess.DataBase import *
from DataAccess.sql_ytb import *
from Web.ytbAccess import *

if __name__ == "__main__":
    ytb_download_video("1-vjAX_aKUQ", abspath(R"./.cache/downloadtest/") + "/",cookie=default_ytb_cookieeditor_ytdlp)
    pass