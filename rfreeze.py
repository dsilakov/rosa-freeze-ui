#!/usr/bin/python

import sys
import os
import locale

from PyQt5.QtWidgets import QApplication, QWidget, QDialog
from PyQt5 import QtCore, QtGui

from ui_rfreeze import Ui_RFreeze

from rosa_freeze import rosa_freeze

# List of root folders that are not mounted over aufs
default_skip_dirs = ['dev', 'home', 'lost+found', 'media', 'mnt', 'proc', 'run', 'sys', 'tmp']

_translate = QtCore.QCoreApplication.translate

class RFreezeUI(QDialog):
    def __init__(self):
        super(RFreezeUI, self).__init__()
        self.ui = Ui_RFreeze()
        self.ui.setupUi(self)
        self.setFixedSize(400,300)
        self.ui.btnExit.clicked.connect(self.exitClicked)
        self.ui.btnEnable.clicked.connect(self.enableClicked)
        self.ui.comboStorage.currentIndexChanged.connect(self.storageChanged)

        for d in default_skip_dirs:
            self.ui.textSkipFolders.append("/" + d)

	self.switchEnableBtnText()
	self.storageChanged()

    def storageIndexToType(self, idx):
        if idx == 0:
            return "tmpfs"
        if idx == 1:
            return "device"
        if idx == 2:
            return "folder"
        return "Unknown"

    def storageChanged(self):
        storageIndex = self.ui.comboStorage.currentIndex();
        storageType = self.storageIndexToType(storageIndex)
        if storageType == "tmpfs":
            grey = "QWidget { background-color:#888888;}"
            self.ui.lineDevName.setStyleSheet(grey)
            self.ui.lineDevName.setEnabled(0)
            self.ui.lineDevName.setPlaceholderText(_translate("RFreeze", "Not applicable"))
        elif storageType == "device":
            white = "QWidget { background-color:#FFFFFF;}"
            self.ui.lineDevName.setStyleSheet(white)
            self.ui.labelDevice.setText(_translate("RFreeze", "Device name:"));
            self.ui.lineDevName.setEnabled(1)
            self.ui.lineDevName.setPlaceholderText(_translate("Enter device name"))
        elif storageType == "folder":
            white = "QWidget { background-color:#FFFFFF;}"
            self.ui.lineDevName.setStyleSheet(white)
            self.ui.labelDevice.setText(_translate("RFreeze", "Folder name:"));
            self.ui.lineDevName.setPlaceholderText(_translate("RFreeze", "Enter folder name"))
            self.ui.lineDevName.setEnabled(1)
            self.ui.lineDevName.setReadOnly(0)

    def exitClicked(self):
        self.close()

    def enableClicked(self):
        if self.currentAction == "Disable":
            res = rosa_freeze.disable_freeze()
            if res == 1:
                print(_translate("RFreeze", "Freeze mode is already disabled"))
            self.switchEnableBtnText()
        elif self.currentAction == "Enable":
            storage = self.ui.comboStorage.currentText();
            storageIndex = self.ui.comboStorage.currentIndex();
	    storageType = self.storageIndexToType(storageIndex)

            if storageType == "device":
                storage = self.ui.lineDevName.text()
                folder = ""
            elif storageType == "tmpfs":
                storage = "tmpfs"
                folder = ""
            elif storageType == "folder":
                storage = "folder"
                folder = self.ui.lineDevName.text()

            skip_lines = self.ui.textSkipFolders.toPlainText()
            skip_dirs = []
            for d in skip_lines.split("\n"):
                if os.path.isdir(d):
                    d = d.replace("/", "", 1)
                    if "/" in d:
                        print(_translate("RFreeze", "Subfolders are not supported, skipping"))
                    else:
                        skip_dirs.append(d)
                elif d != "":
                    print(_translate("RFreeze", "Not a directory, skipping: ") + d)

            res = rosa_freeze.enable_freeze(skip_dirs, storage, folder)
            if res == 2:
                print(_translate("RFreeze", "Freeze mode is already enabled"))
            elif res == 3:
                print(_translate("RFreeze", "Freeze mode was disabled but the system was not rebooted after that"))
            elif res == 4:
                print(_translate("RFreeze", "failed to get UUID for the storage device"))
            elif res == 5:
                print(_translate("RFreeze", "storage device is already mounted"))
            elif res == 61:
                print(_translate("RFreeze", "path to the folder is not absolute"))
            elif res == 62:
                print(_translate("RFreeze", "can't determine top-level parent for the folder"))
            elif res == 99:
                print(_translate("RFreeze", "smth went wrong during 'os.system' run"))
            self.switchEnableBtnText()

    def switchEnableBtnText(self):
        state = rosa_freeze.get_status()
        if state == "enabled":
            self.ui.btnEnable.setText(_translate("RFreeze", "Disable"))
            self.ui.btnEnable.setEnabled(1)
            self.currentAction = "Disable"
        elif state == "disabled":
            self.ui.btnEnable.setText(_translate("RFreeze", "Enable"))
            self.ui.btnEnable.setEnabled(1)
            self.currentAction = "Enable"
        else:
            self.ui.btnEnable.setText(_translate("RFreeze", "!Reboot"))
            self.ui.btnEnable.setEnabled(0)
            self.currentAction = "Reboot"

def main():
    app = QApplication(sys.argv)

    translator = QtCore.QTranslator(app)
    translator.load("RFreeze_" + locale.getlocale()[0] + ".qm", ".")
    app.installTranslator(translator)

    w = QWidget()
    ui = RFreezeUI()
    ui.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
