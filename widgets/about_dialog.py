# -*- coding: utf-8 -*-
# @Author  : LG


from ui.about_dialog import Ui_Dialog
from PyQt5 import QtWidgets, QtCore


class AboutDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
