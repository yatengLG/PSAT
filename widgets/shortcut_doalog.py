# -*- coding: utf-8 -*-
# @Author  : LG

from ui.shortcut_dialog import Ui_Dialog
from PyQt5 import QtWidgets, QtCore


class ShortCutDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent):
        super(ShortCutDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
