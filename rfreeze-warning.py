#!/usr/bin/python

import sys
import os
import locale
import subprocess

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMessageBox, QWidget
from PyQt5 import QtCore, QtGui

from rosa_freeze_ui import rc_rfreeze

_translate = QtCore.QCoreApplication.translate

def main():
    app = QApplication(sys.argv)

    w = QWidget()
    skip_dirs_str = subprocess.Popen("sed 's/.*rfreeze_skip_dirs=\\(\\S*\\) .*$/\\1/' /proc/cmdline", shell=True, stdout=subprocess.PIPE).stdout.read()
    skip_dirs = skip_dirs_str.rstrip().split(":")
    skip_dirs_msg = ""
    for d in skip_dirs:
        skip_dirs_msg += "/" + d + "\n"

    q = QMessageBox()
    q.setWindowTitle(_translate("RFreeze", "ROSA Freeze is enabled!"))
    q.setText(_translate("RFreeze", "ROSA Freeze is enabled in your system."))
    q.setInformativeText(_translate("RFreeze", "All changes in the system will be lost after reboot except modifications of the following folders:\n" + skip_dirs_msg))
    q.setIconPixmap(QtGui.QPixmap(":/images/rosa-freeze-64.png"))
    sys.exit(q.exec_())

if __name__ == '__main__':
    main()