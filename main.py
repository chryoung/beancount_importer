#!/usr/bin/env python3

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from main_window import MainWindow

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.setupUi()
main_window.show()

sys.exit(app.exec_())
