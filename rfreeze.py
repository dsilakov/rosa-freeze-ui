#!/usr/bin/python

import sys
import os
import locale

from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QFileDialog, QMessageBox, QGridLayout, QProgressBar, QLabel
from PyQt5 import QtCore, QtGui

from rosa_freeze_ui.ui_rfreeze import Ui_RFreeze
from rosa_freeze_ui import rc_rfreeze

from rosa_freeze import rosa_freeze
from rosa_freeze.config import Config

cfg = Config()

# List of root folders that are not mounted over aufs
default_skip_dirs = cfg['freeze']['skip_dirs'].split()

_translate = QtCore.QCoreApplication.translate

# Thread to call "rfreeze enable"
class EnableThread(QtCore.QThread):
    signalFinished = QtCore.pyqtSignal(int)

    def __init__(self, skip_dirs, storage, folder):
	QtCore.QThread.__init__(self)
	self.skip_dirs = skip_dirs
	self.storage = storage
	self.folder = folder

    def __del__(self):
	self.wait()

    def run(self):
        res = rosa_freeze.enable_freeze(self.skip_dirs, self.storage, self.folder)
        self.signalFinished.emit(res)

# Thread to call "rfreeze disable"
class DisableThread(QtCore.QThread):
    signalFinished = QtCore.pyqtSignal(int)

    def __init__(self):
	QtCore.QThread.__init__(self)

    def __del__(self):
	self.wait()

    def run(self):
        res = rosa_freeze.disable_freeze()
        self.signalFinished.emit(res)

# Thread to call "rfreeze merge"
class MergeThread(QtCore.QThread):
    signalFinished = QtCore.pyqtSignal(int)

    def __init__(self):
	QtCore.QThread.__init__(self)

    def __del__(self):
	self.wait()

    def run(self):
        res = rosa_freeze.merge_state()
        self.signalFinished.emit(res)

# Main class
class RFreezeUI(QDialog):
    def __init__(self):
        super(RFreezeUI, self).__init__()
        self.ui = Ui_RFreeze()
        self.ui.setupUi(self)
        self.ui.btnExit.clicked.connect(self.exitClicked)
        self.ui.btnEnable.clicked.connect(self.enableClicked)
        self.ui.btnMerge.clicked.connect(self.mergeClicked)
        self.ui.btnAddFolder.clicked.connect(self.addFolderClicked)
        self.ui.btnRmFolder.clicked.connect(self.rmFolderClicked)
        self.ui.comboStorage.currentIndexChanged.connect(self.storageChanged)

        for d in default_skip_dirs:
            self.ui.folderList.addItem("/" + d)

	self.switchEnableBtnText()
	self.storageChanged()

        self.ui.busyBar.setMaximum(0)
        self.ui.busyBar.setMinimum(0)
        self.ui.busyBar.setVisible(0)
        self.ui.busyLabel.setVisible(0)

    # given index in combobox, return storage type
    # not gracefull, so do not resort items in combobox!
    def storageIndexToType(self, idx):
        if idx == 0:
            return "tmpfs"
        if idx == 1:
            return "device"
        if idx == 2:
            return "folder"
        return "Unknown"

    # user has chosen another storage type - let's check if 
    # we should enble text field where he will enter device or folder name
    # and adjust text in the label accordingly
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

    def mergeClicked(self):
	self.switchBusyIndicator(True)
	self.workThread = MergeThread()
	self.workThread.signalFinished.connect(self.mergeFinishedEvent)
	self.workThread.start()

    def enableClicked(self):
	self.switchBusyIndicator(True)

        if self.currentAction == "Disable":
	    self.workThread = DisableThread()
	    self.workThread.signalFinished.connect(self.disableFinishedEvent)
	    self.workThread.start()

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
                        QMessageBox.warning(self,
    					_translate("RFreeze", "Freeze Warning"),
    					_translate("RFreeze", "Subfolders are not supported, skipping") + ": " + d,
    					QMessageBox.Ok
    				    )
                    else:
                        skip_dirs.append(d)
                elif d != "":
                    QMessageBox.warning(self,
    					_translate("RFreeze", "Freeze Warning"),
    					_translate("RFreeze", "Not a directory, skipping: ") + d,
    					QMessageBox.Ok
    				    )

	    self.workThread = EnableThread(skip_dirs, storage, folder)
	    self.workThread.signalFinished.connect(self.enableFinishedEvent)
	    self.workThread.start()


    def switchBusyIndicator(self, enable=True):
        # If busy indicator is enable, all control elements must be disable and vice versa
        enableItems = not enable
        self.ui.busyBar.setVisible(enable)
        self.ui.busyLabel.setVisible(enable)

        self.ui.btnExit.setEnabled(enableItems)
        self.ui.btnEnable.setEnabled(enableItems)
        self.ui.btnAddFolder.setEnabled(enableItems)
        self.ui.btnRmFolder.setEnabled(enableItems)
        self.ui.comboStorage.setEnabled(enableItems)
        self.ui.btnMerge.setEnabled(enableItems)
        self.ui.folderList.setEnabled(enableItems)


    def mergeFinishedEvent(self, res):
	if res == 0:
            QMessageBox.information(self,
				_translate("RFreeze", "Success!"),
				_translate("RFreeze", "The current state of the system has been saved as the base one."),
				QMessageBox.Ok
			    )
        elif res == 1:
            QMessageBox.warning(self,
				_translate("RFreeze", "Merge Error"),
				_translate("RFreeze", "You don't have ROSA Freeze enabled"),
				QMessageBox.Ok
			    )
        else:
            QMessageBox.warning(self,
				_translate("RFreeze", "Merge Error"),
				_translate("RFreeze", "Something went wrong during merge, please inform developers..."),
				QMessageBox.Ok
			    )
    	self.switchBusyIndicator(False)
        self.switchEnableBtnText()

    def disableFinishedEvent(self, res):
	if res == 0:
            QMessageBox.information(self,
				_translate("RFreeze", "Success!"),
				_translate("RFreeze", "Freeze mode has been successfully disabled. Please reboot your computer to work in a normal mode."),
				QMessageBox.Ok
			    )
        elif res == 1:
            QMessageBox.warning(self,
    					_translate("RFreeze", "Freeze Error"),
    					_translate("RFreeze", "Freeze mode is already disabled"),
    					QMessageBox.Ok
    				    )
    	self.switchBusyIndicator(False)
        self.switchEnableBtnText()


    def enableFinishedEvent(self, res):
	if res == 0:
            QMessageBox.information(self,
				_translate("RFreeze", "Success!"),
				_translate("RFreeze", "Freeze mode has been successfully enabled."),
				QMessageBox.Ok
			    )
        elif res == 2:
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
            QMessageBox.warning(self.ui,
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
    	self.switchBusyIndicator(False)
        self.switchEnableBtnText()

    # Check current freeze state and depending on it
    # change text on buttons and enable/disable different elements
    def switchEnableBtnText(self):
        state = rosa_freeze.get_status()
        if state == "enabled":
            self.ui.btnEnable.setText(_translate("RFreeze", "Disable"))
            self.ui.btnEnable.setEnabled(1)
            self.ui.label_status.setText(_translate("RFreeze", "Enabled"))
            self.ui.folderList.setEnabled(0)
            self.ui.btnAddFolder.setEnabled(0)
            self.ui.btnRmFolder.setEnabled(0)
            self.ui.comboStorage.setEnabled(0)
            self.ui.btnMerge.setEnabled(1)
            self.currentAction = "Disable"
        elif state == "disabled":
            self.ui.btnEnable.setText(_translate("RFreeze", "Enable"))
            self.ui.btnEnable.setEnabled(1)
            self.ui.label_status.setText(_translate("RFreeze", "Disabled"))
            self.ui.folderList.setEnabled(1)
            self.ui.btnAddFolder.setEnabled(1)
            self.ui.btnRmFolder.setEnabled(1)
            self.ui.comboStorage.setEnabled(1)
            self.ui.btnMerge.setEnabled(0)
            self.currentAction = "Enable"
        else:
            self.ui.btnEnable.setText(_translate("RFreeze", "!Reboot"))
            self.ui.btnEnable.setEnabled(0)
            self.ui.label_status.setText(_translate("RFreeze", "Reboot required"))
            self.ui.folderList.setEnabled(0)
            self.ui.btnAddFolder.setEnabled(0)
            self.ui.btnRmFolder.setEnabled(0)
            self.ui.btnMerge.setEnabled(0)
            self.ui.comboStorage.setEnabled(0)
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
