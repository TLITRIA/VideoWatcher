from UI.excludeReasonDialog import *

from PyQt6.QtWidgets import QDialog
from Widget.InfoWidget import InfoWidget
from PyQt6.QtCore import pyqtSignal
from DataAccess.sql_query import *


class UpExcludeReasonDialog(QDialog, Ui_Dialog):
    iw: InfoWidget
    def __init__(self, w:InfoWidget, parent=None):
        super(UpExcludeReasonDialog, self).__init__(parent)
        self.setupUi(self)
        self.iw = w

    def on_textchanged(self):
        text = self.plainTextEdit.toPlainText()
        

