# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/super/PycharmProjects/PSAT/ui/shortcut_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(550, 280)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(550, 280))
        Dialog.setMaximumSize(QtCore.QSize(550, 280))
        font = QtGui.QFont()
        font.setKerning(True)
        Dialog.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setMinimumSize(QtCore.QSize(0, 60))
        self.widget.setMaximumSize(QtCore.QSize(16777215, 60))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout.addWidget(self.widget)
        self.widget_2 = QtWidgets.QWidget(Dialog)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        self.widget_2.setFont(font)
        self.widget_2.setObjectName("widget_2")
        self.gridLayout = QtWidgets.QGridLayout(self.widget_2)
        self.gridLayout.setObjectName("gridLayout")
        self.label_6 = QtWidgets.QLabel(self.widget_2)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 0, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.widget_2)
        self.label_12.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_12.setStyleSheet("color: rgb(133, 0, 0);")
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 0, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.widget_2)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 0, 2, 1, 1)
        self.label_19 = QtWidgets.QLabel(self.widget_2)
        self.label_19.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_19.setStyleSheet("color: rgb(133, 0, 0);")
        self.label_19.setObjectName("label_19")
        self.gridLayout.addWidget(self.label_19, 0, 3, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.widget_2)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.widget_2)
        self.label_13.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_13.setStyleSheet("color: rgb(133, 0, 0);")
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 1, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.widget_2)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 2, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.widget_2)
        self.label_18.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_18.setStyleSheet("color: rgb(133, 0, 0);")
        self.label_18.setObjectName("label_18")
        self.gridLayout.addWidget(self.label_18, 1, 3, 1, 1)
        self.label_24 = QtWidgets.QLabel(self.widget_2)
        self.label_24.setObjectName("label_24")
        self.gridLayout.addWidget(self.label_24, 2, 0, 1, 1)
        self.label_28 = QtWidgets.QLabel(self.widget_2)
        self.label_28.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_28.setStyleSheet("color: rgb(133, 0, 0);")
        self.label_28.setObjectName("label_28")
        self.gridLayout.addWidget(self.label_28, 2, 1, 1, 1)
        self.label_25 = QtWidgets.QLabel(self.widget_2)
        self.label_25.setObjectName("label_25")
        self.gridLayout.addWidget(self.label_25, 2, 2, 1, 1)
        self.label_30 = QtWidgets.QLabel(self.widget_2)
        self.label_30.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_30.setStyleSheet("color: rgb(133, 0, 0);")
        self.label_30.setObjectName("label_30")
        self.gridLayout.addWidget(self.label_30, 2, 3, 1, 1)
        self.label_26 = QtWidgets.QLabel(self.widget_2)
        self.label_26.setObjectName("label_26")
        self.gridLayout.addWidget(self.label_26, 3, 0, 1, 1)
        self.label_29 = QtWidgets.QLabel(self.widget_2)
        self.label_29.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_29.setStyleSheet("color: rgb(133, 0, 0);")
        self.label_29.setObjectName("label_29")
        self.gridLayout.addWidget(self.label_29, 3, 1, 1, 1)
        self.label_27 = QtWidgets.QLabel(self.widget_2)
        self.label_27.setObjectName("label_27")
        self.gridLayout.addWidget(self.label_27, 3, 2, 1, 1)
        self.label_31 = QtWidgets.QLabel(self.widget_2)
        self.label_31.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_31.setStyleSheet("color: rgb(133, 0, 0);")
        self.label_31.setObjectName("label_31")
        self.gridLayout.addWidget(self.label_31, 3, 3, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.widget_2)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 4, 0, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.widget_2)
        self.label_15.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_15.setStyleSheet("color: rgb(133, 0, 0);")
        self.label_15.setObjectName("label_15")
        self.gridLayout.addWidget(self.label_15, 4, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.widget_2)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 4, 2, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.widget_2)
        self.label_20.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_20.setStyleSheet("color: rgb(133, 0, 0);")
        self.label_20.setObjectName("label_20")
        self.gridLayout.addWidget(self.label_20, 4, 3, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.widget_2)
        self.label_14.setObjectName("label_14")
        self.gridLayout.addWidget(self.label_14, 5, 0, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.widget_2)
        self.label_16.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_16.setStyleSheet("color: rgb(133, 0, 0);")
        self.label_16.setObjectName("label_16")
        self.gridLayout.addWidget(self.label_16, 5, 1, 1, 1)
        self.label_22 = QtWidgets.QLabel(self.widget_2)
        self.label_22.setObjectName("label_22")
        self.gridLayout.addWidget(self.label_22, 6, 0, 1, 1)
        self.label_23 = QtWidgets.QLabel(self.widget_2)
        self.label_23.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_23.setStyleSheet("color: rgb(133, 0, 0);")
        self.label_23.setObjectName("label_23")
        self.gridLayout.addWidget(self.label_23, 6, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.widget_2)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 6, 2, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.widget_2)
        self.label_21.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_21.setStyleSheet("color: rgb(133, 0, 0);")
        self.label_21.setObjectName("label_21")
        self.gridLayout.addWidget(self.label_21, 6, 3, 1, 1)
        self.verticalLayout.addWidget(self.widget_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "help"))
        self.label.setText(_translate("Dialog", "Shortcut"))
        self.label_6.setText(_translate("Dialog", "Open file"))
        self.label_12.setText(_translate("Dialog", "W"))
        self.label_10.setText(_translate("Dialog", "Save annotation"))
        self.label_19.setText(_translate("Dialog", "S"))
        self.label_4.setText(_translate("Dialog", "Start polygon pick"))
        self.label_13.setText(_translate("Dialog", "C"))
        self.label_5.setText(_translate("Dialog", "Cache polygon pick"))
        self.label_18.setText(_translate("Dialog", "Esc"))
        self.label_24.setText(_translate("Dialog", "Elevation "))
        self.label_28.setText(_translate("Dialog", "1"))
        self.label_25.setText(_translate("Dialog", "RGB"))
        self.label_30.setText(_translate("Dialog", "2"))
        self.label_26.setText(_translate("Dialog", "Category"))
        self.label_29.setText(_translate("Dialog", "3"))
        self.label_27.setText(_translate("Dialog", "Instance"))
        self.label_31.setText(_translate("Dialog", "4"))
        self.label_8.setText(_translate("Dialog", "To top view"))
        self.label_15.setText(_translate("Dialog", "T"))
        self.label_9.setText(_translate("Dialog", "To front view"))
        self.label_20.setText(_translate("Dialog", "F"))
        self.label_14.setText(_translate("Dialog", "To right view"))
        self.label_16.setText(_translate("Dialog", "R"))
        self.label_22.setText(_translate("Dialog", "Point size +"))
        self.label_23.setText(_translate("Dialog", "="))
        self.label_11.setText(_translate("Dialog", "Point size -"))
        self.label_21.setText(_translate("Dialog", "-"))
