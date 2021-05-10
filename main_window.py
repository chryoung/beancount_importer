from os import path

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog

from config import app_config
from select_account_dialog import SelectAccountDialog
from select_currency_dialog import SelectCurrencyDialog
from ui_main_window import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.beancount_file = ''
        self.setup_dialog(self.beancount_file)

    def setupUi(self):
        self.ui.setupUi(self)
        self.ui.openBeancountAccountAction.triggered.connect(self.select_beancount_file)
        self.ui.selectPaymentAccountBtn.clicked.connect(self.select_default_payment_account)
        self.ui.selectExpensesAccountBtn.clicked.connect(self.select_default_expenses_account)
        self.ui.selectCurrencyBtn.clicked.connect(self.select_default_currency)

    def setup_dialog(self, beancount_file: str):
        self.select_account_dialog = SelectAccountDialog(beancount_file, parent=self)
        self.select_account_dialog.setupUi()
        self.select_currency_dialog = SelectCurrencyDialog(beancount_file)
        self.select_currency_dialog.setupUi()

    def select_beancount_file(self):
        recent_beancount_path = path.dirname(app_config.recent_beancount_file)
        self.beancount_file = QFileDialog.getOpenFileName(self, 'Open beancount file', recent_beancount_path,
                                                          'beancount (*.beancount *.bc *.txt)')[0]
        app_config.recent_beancount_file = self.beancount_file
        self.setup_dialog(self.beancount_file)

    def select_default_payment_account(self):
        if self.select_account_dialog.exec() == QDialog.Accepted:
            self.ui.defaultPaymentAccountLE.setText(self.select_account_dialog.get_selected_account())

    def select_default_expenses_account(self):
        if self.select_account_dialog.exec() == QDialog.Accepted:
            self.ui.defaultExpensesAccountLE.setText(self.select_account_dialog.get_selected_account())

    def select_default_currency(self):
        if self.select_currency_dialog.exec() == QDialog.Accepted:
            self.ui.defaultCurrencyLE.setText(self.select_currency_dialog.get_selected_currency())
