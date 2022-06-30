#!/usr/bin/env python3

import logging
import logging.handlers
import sys

from PyQt6.QtWidgets import QApplication

from config import app_config
from gui.main_window import MainWindow


def init_logger():
    log_fh = logging.handlers.RotatingFileHandler('runtime.log', encoding='utf-8', maxBytes=2*1024*1024, backupCount=5)
    log_fh.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s]%(message)s'))
    logging.getLogger().addHandler(log_fh)
    logging.getLogger().setLevel(logging.DEBUG)


def on_last_window_closed():
    app_config.save()


if __name__ == '__main__':
    init_logger()
    app = QApplication(sys.argv)
    app.lastWindowClosed.connect(on_last_window_closed)

    logging.info('Initialise main window.')
    main_window = MainWindow()
    main_window.setupUi()
    main_window.setup_beancount_option(app_config.recent_beancount_file)
    main_window.show()

    logging.info('Exit.')
    sys.exit(app.exec())
