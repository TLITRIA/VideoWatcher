import os, sys
from Widget.InfoWidget import *
from PyQt6.QtWidgets import QApplication
from DataAccess.DataBase import *
from DataAccess.sql_query import *

'''
infowidget 是最小的信息显示单元
显示视频信息作者信息及其相互关系

todo 找到所有初始化位置

初始化作者信息、视频信息其中至少一项
作者信息：至少需要作者id，作者名称
视频信息：至少需要视频id
其他信息：所属文件夹名称。这个不应该与infowidget绑定，应该和playlistwidget绑定
初始化方式：
    1提供关键信息，其他从数据库中搜索
    2提供series，自动解析
'''
def main():
    app = QApplication(sys.argv)
    db = DataBase()
    db.Connect(videowatcher_sql_fp)


    w = InfoWidget()
    
    sys.exit(app.exec())


