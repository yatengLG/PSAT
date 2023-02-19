# -*- coding: utf-8 -*-
# @Author  : LG

from PyQt5 import QtCore, QtWidgets, QtGui
from ui.category_choice import Ui_Dialog


class CategoryChoiceDialog(QtWidgets.QDialog, Ui_Dialog):
    category_instance = QtCore.pyqtSignal(str, int)
    def __init__(self, parent, mainwindow):
        super(CategoryChoiceDialog, self).__init__(parent)
        self.mainwindow = mainwindow

        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        regExp = QtCore.QRegExp('^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])$')
        self.lineEdit_group.setValidator(QtGui.QRegExpValidator(regExp))

        self.listWidget.itemClicked.connect(self.get_category)
        self.pushButton_apply.clicked.connect(self.apply)
        self.pushButton_cache.clicked.connect(self.cache)

        self.category_instance.connect(self.mainwindow.openGLWidget.polygon_pick)

    def load_cfg(self):
        self.listWidget.clear()

        labels = self.mainwindow.cfg.get('label', [])

        for label in labels:
            name = label.get('name', '__unclassified__')
            color = label.get('color', '#ffffff')
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(QtCore.QSize(200, 30))
            widget = QtWidgets.QWidget()

            layout = QtWidgets.QHBoxLayout()
            layout.setContentsMargins(9, 1, 9, 1)
            label_category = QtWidgets.QLabel()
            label_category.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            label_category.setText(name)
            label_category.setObjectName('label_category')

            label_color = QtWidgets.QLabel()
            label_color.setFixedWidth(10)
            label_color.setStyleSheet("background-color: {};".format(color))
            label_color.setObjectName('label_color')

            layout.addWidget(label_color)
            layout.addWidget(label_category)
            widget.setLayout(layout)

            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)

        self.lineEdit_group.clear()
        self.lineEdit_category.clear()

        if self.listWidget.count() == 0:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Please set categorys before tagging.')

    def get_category(self, item):
        widget = self.listWidget.itemWidget(item)
        label_category = widget.findChild(QtWidgets.QLabel, 'label_category')
        self.lineEdit_category.setText(label_category.text())
        self.lineEdit_category.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def apply(self):
        category = self.lineEdit_category.text()
        group = self.lineEdit_group.text()
        if not category:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Please select one category before submitting.')
            return

        group = int(group) if group else None
        print('category: ', category)
        print('group: ', group)
        self.mainwindow.openGLWidget.polygon_pick(category, group)
        # self.category_instance.emit(category, group)

        self.mainwindow.openGLWidget.change_mode_to_view()
        self.close()

    def cache(self):
        self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent):
        self.cache()

    def reject(self):
        self.cache()