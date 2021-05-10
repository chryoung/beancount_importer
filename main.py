#!/usr/bin/env python3

import sys

from PyQt5.QtWidgets import QApplication

from config import app_config
from main_window import MainWindow


def on_last_window_closed():
    app_config.save()


app = QApplication(sys.argv)
app.lastWindowClosed.connect(on_last_window_closed)
main_window = MainWindow()
main_window.setupUi()
main_window.show()

sys.exit(app.exec_())
