# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rfreeze.ui'
#
# Created: Tue Feb  3 09:25:55 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_RFreeze(object):
    def setupUi(self, RFreeze):
        RFreeze.setObjectName("RFreeze")
        RFreeze.resize(400, 300)
        RFreeze.setMinimumSize(QtCore.QSize(400, 0))
        RFreeze.setSizeGripEnabled(True)
        self.btnEnable = QtWidgets.QPushButton(RFreeze)
        self.btnEnable.setGeometry(QtCore.QRect(300, 30, 81, 31))
        self.btnEnable.setObjectName("btnEnable")
        self.btnExit = QtWidgets.QPushButton(RFreeze)
        self.btnExit.setGeometry(QtCore.QRect(300, 70, 81, 31))
        self.btnExit.setObjectName("btnExit")
        self.horizontalLayoutWidget = QtWidgets.QWidget(RFreeze)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 60, 261, 31))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelDevice = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.labelDevice.setMinimumSize(QtCore.QSize(100, 0))
        self.labelDevice.setObjectName("labelDevice")
        self.horizontalLayout.addWidget(self.labelDevice)
        self.lineDevName = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.lineDevName.setObjectName("lineDevName")
        self.horizontalLayout.addWidget(self.lineDevName)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(RFreeze)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(20, 30, 261, 31))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.comboStorage = QtWidgets.QComboBox(self.horizontalLayoutWidget_2)
        self.comboStorage.setObjectName("comboStorage")
        self.comboStorage.addItem("")
        self.comboStorage.addItem("")
        self.comboStorage.addItem("")
        self.horizontalLayout_2.addWidget(self.comboStorage)
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(RFreeze)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(20, 90, 261, 181))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        self.label_2.setMinimumSize(QtCore.QSize(100, 0))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.textSkipFolders = QtWidgets.QTextEdit(self.horizontalLayoutWidget_3)
        self.textSkipFolders.setObjectName("textSkipFolders")
        self.horizontalLayout_3.addWidget(self.textSkipFolders)

        self.retranslateUi(RFreeze)
        QtCore.QMetaObject.connectSlotsByName(RFreeze)

    def retranslateUi(self, RFreeze):
        _translate = QtCore.QCoreApplication.translate
        RFreeze.setWindowTitle(_translate("RFreeze", "ROSA Freeze"))
        self.btnEnable.setText(_translate("RFreeze", "Enable"))
        self.btnExit.setText(_translate("RFreeze", "Exit"))
        self.labelDevice.setText(_translate("RFreeze", "Device name:"))
        self.label.setText(_translate("RFreeze", "Storage:"))
        self.comboStorage.setItemText(0, _translate("RFreeze", "tmpfs"))
        self.comboStorage.setItemText(1, _translate("RFreeze", "device"))
        self.comboStorage.setItemText(2, _translate("RFreeze", "folder"))
        self.label_2.setText(_translate("RFreeze", "Folders to skip:"))

