import os, sys
from Widget.EntryWidget import *
from Web.MyWebDriver import *
from DataAccess.DataBase import *
from DataAccess.sql_query import *
from PyQt6.QtWidgets import QApplication
from Web.biliAccess import *

from Common.Logger import *

'''
测试entrywidget能否正确解析指定页面
'''
def main():
    app = QApplication(sys.argv)

    wd = MyWebDriver()
    wd.Login()

    db = DataBase()
    db.Connect(videowatcher_sql_fp)
    create_all(db, videowatcher_sqls)

    v = EntryWidget()
    # v.setWindowState(Qt.WindowState.WindowMaximized)
    v.show()

    url_bili_video ="https://www.bilibili.com/video/BV15cuV6pEnY/?spm_id_from=333.1007.tianma.1-1-1.click&vd_source=eb37b7b47eaa888d1299c60038fb6205"
    url_bili_upspace = 'https://space.bilibili.com/583393248/upload/video'




    '''
    bilibiliup主主页的视频发布页，解析up主信息
    '''
    with timeblock('前往并解析up主主页'):
        v.goto(url_bili_upspace)
    input('press any key to continue...')

    '''
    bilibili视频页，解析视频信息、相关信息、视频简介和评论中的url链接
    必须找一个简介和评论区都有链接的视频
    '''
    with timeblock('前往并解析视频页'):
        v.goto(url_bili_video)
    input('press any key to continue...')

    '''
    bili收藏夹页面，用户默认收藏夹
    '''
    with timeblock('前往并解析用户默认收藏夹'):
        goto_default_collectfolder(wd)
        v.focus()
    input('press any key to continue...')

    sys.exit(app.exec())
