#!/usr/bin/python

import sys
import os
import locale

from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QFileDialog, QMessageBox
from PyQt5 import QtCore, QtGui

from rosa_freeze_ui.ui_rfreeze import Ui_RFreeze
from rosa_freeze_ui import rc_rfreeze

from rosa_freeze import rosa_freeze

# List of root folders that are not mounted over aufs
default_skip_dirs = ['dev', 'home', 'lost+found', 'media', 'mnt', 'proc', 'run', 'sys', 'tmp']

_translate = QtCore.QCoreApplication.translate

class RFreezeUI(QDialog):
    def __init__(self):
        super(RFreezeUI, self).__init__()
        self.ui = Ui_RFreeze()
        self.ui.setupUi(self)
        self.ui.btnExit.clicked.connect(self.exitClicked)
        self.ui.btnEnable.clicked.connect(self.enableClicked)
        self.ui.btnAddFolder.clicked.connect(self.addFolderClicked)
        self.ui.btnRmFolder.clicked.connect(self.rmFolderClicked)
        self.ui.comboStorage.currentIndexChanged.connect(self.storageChanged)

        for d in default_skip_dirs:
            self.ui.folderList.addItem("/" + d)

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
            self.ui.lineDevName.setPlaceholderText(_translate("RFreeze", "Enter device name"))
        elif storageType == "folder":
            white = "QWidget { background-color:#FFFFFF;}"
            self.ui.lineDevName.setStyleSheet(white)
            self.ui.labelDevice.setText(_translate("RFreeze", "Folder name:"));
            self.ui.lineDevName.setPlaceholderText(_translate("RFreeze", "Enter folder name"))
            self.ui.lineDevName.setEnabled(1)
            self.ui.lineDevName.setReadOnly(0)

    def exitClicked(self):
        self.close()

    def addFolderClicked(self):
        new_dir = str(QFileDialog.getExistingDirectory(self,_translate("RFreeze", "Select Directory"), "/"))

	d = new_dir
        d = d.replace("/", "", 1)
        if "/" in d:
            QMessageBox.warning(self,
    					_translate("RFreeze", "Can't choose subfolder"),
    					_translate("RFreeze", "Subfolders are not supported, you can choose only top-level directories"),
    					QMessageBox.Ok
    				    )
            return 1

        exists = self.ui.folderList.findItems(new_dir, QtCore.Qt.MatchExactly)
        if not exists:
            self.ui.folderList.addItem(new_dir)
            self.ui.folderList.sortItems()

    def rmFolderClicked(self):
        for i in self.ui.folderList.selectedItems():
            self.ui.folderList.takeItem(self.ui.folderList.row(i))

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

            skip_dirs = []
            for i in xrange(self.ui.folderList.count()):
                d = self.ui.folderList.item(i).text()
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
                QMessageBox.warning(self,
    					_translate("RFreeze", "Freeze Error"),
    					_translate("RFreeze", "Freeze mode is already enabled"),
    					QMessageBox.Ok
    				    )
            elif res == 3:
                QMessageBox.warning(self,
    					_translate("RFreeze", "Freeze Error"),
    					_translate("RFreeze", "Freeze mode was disabled but the system was not rebooted after that"),
    					QMessageBox.Ok
    				    )
            elif res == 4:
                QMessageBox.warning(self,
    					_translate("RFreeze", "Freeze Error"),
    					_translate("RFreeze", "failed to get UUID for the storage device"),
    					QMessageBox.Ok
    				    )
            elif res == 5:
                QMessageBox.warning(self,
    					_translate("RFreeze", "Freeze Error"),
    					_translate("RFreeze", "storage device is already mounted"),
    					QMessageBox.Ok
    				    )
            elif res == 61:
                QMessageBox.warning(self,
    					_translate("RFreeze", "Freeze Error"),
    					_translate("RFreeze", "path to the folder is not absolute"),
    					QMessageBox.Ok
    				    )
            elif res == 62:
                QMessageBox.warning(self,
    					_translate("RFreeze", "Freeze Error"),
    					_translate("RFreeze", "can't determine top-level parent for the folder"),
    					QMessageBox.Ok
    				    )
            elif res == 99:
                QMessageBox.warning(self,
    					_translate("RFreeze", "Freeze Error"),
    					_translate("RFreeze", "smth went wrong during 'os.system' run"),
    					QMessageBox.Ok
    				    )
            self.switchEnableBtnText()

    def switchEnableBtnText(self):
        state = rosa_freeze.get_status()
        if state == "enabled":
            self.ui.btnEnable.setText(_translate("RFreeze", "Disable"))
            self.ui.btnEnable.setEnabled(1)
            self.ui.label_status.setText(_translate("RFreeze", "Enabled"))
            self.currentAction = "Disable"
        elif state == "disabled":
            self.ui.btnEnable.setText(_translate("RFreeze", "Enable"))
            self.ui.btnEnable.setEnabled(1)
            self.ui.label_status.setText(_translate("RFreeze", "Disabled"))
            self.currentAction = "Enable"
        else:
            self.ui.btnEnable.setText(_translate("RFreeze", "!Reboot"))
            self.ui.btnEnable.setEnabled(0)
            self.ui.label_status.setText(_translate("RFreeze", "Reboot required"))
            self.currentAction = "Reboot"

def main():
    app = QApplication(sys.argv)

    translator = QtCore.QTranslator(app)
    translator.load("RFreeze_" + locale.getlocale()[0] + ".qm", "/usr/share/rosa-freeze-ui/i18n")
    app.installTranslator(translator)

    w = QWidget()
    ui = RFreezeUI()
    ui.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
