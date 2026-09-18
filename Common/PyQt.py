import os, sys
from os.path import abspath
from urllib.request import urlretrieve
from Common.Common import *
import shutil

def dlHash(url:str, filename:str = 'tmp.png'):
    '''
    下载图片到本地以显示
    '''
    local_fold = abspath(R"./.cache/picture/")
    fp = os.path.join(local_fold, filename)
    if not os.path.exists(fp):
        g_mkdir_byfp(fp)
    urlretrieve(url, fp)
    # 按照文件hash名重命名
    newname = get_file_hash(fp) + '.jpg'
    new_fp = os.path.join(local_fold, newname)
    shutil.copy(fp, new_fp)
    return new_fp

def dlCache(url:str):
    ...


from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


def register_webImg(label:QLabel, url:str):
    network_manager = QNetworkAccessManager()
    
    def on_image_loaded(reply:QNetworkReply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data = reply.readAll()
            image = QPixmap()
            if image.loadFromData(data):
                image = image.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio)
                label.setPixmap(image)
            else:
                label.setText("Failed to load image")
        else:
            label.setText("Network error: " + reply.errorString())
        reply.deleteLater()

    def cancel_download():
        try:
            network_manager.disconnect()
            print("Download cancelled")
        except:
            pass

    network_manager.finished.connect(on_image_loaded)
    label.destroyed.connect(cancel_download)
    request = QNetworkRequest(QUrl(url))
    network_manager.get(request)
    