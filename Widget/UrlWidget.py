from UI.urlForm import Ui_Form
from os.path import abspath
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal


class UrlWidget(QWidget, Ui_Form):
    s_goto = pyqtSignal(str)
    def on_clickGoto(self):
        self.s_goto.emit(self.label.text())
    def __init__(self, url, parent=None):
        super(UrlWidget, self).__init__(parent)
        self.setupUi(self)
        self.label.setText(url)
        self.pushButton.setIcon(QIcon(abspath(r"./Resource/rarrow.png")))
        self.pushButton.clicked.connect(self.on_clickGoto)