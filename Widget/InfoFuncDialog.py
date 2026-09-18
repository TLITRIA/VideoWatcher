from UI.infoFuncDialog import *

from PyQt6.QtWidgets import QDialog
from Widget.InfoWidget import InfoWidget
from PyQt6.QtCore import pyqtSignal
from Web.biliAccess import *
from Common.Process import *


class InfoFuncDialog(QDialog, Ui_Dialog):
    iw: InfoWidget
    # s_del_infoW = pyqtSignal(InfoWidget)

    def __init__(self, w: InfoWidget, parent=None):
        super(InfoFuncDialog, self).__init__(parent)
        self.setupUi(self)
        self.iw = w

    def on_remove_widget(self):
        self.iw.s_del_infoW.emit(self.iw)
        self.close()

    def on_remove_video(self):
        if not self.iw._fold_name:
            return
        pm: ProcessManager = ProcessManager()
        pm.AddTask(
            remove_video_fromFold,
            *[[[self.iw._v_id, self.iw._fold_name]]]
        )
        self.on_remove_widget()
