from os import path
from typing import List, Callable

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog, QMessageBox

from alipay import get_transactions_from_alipay_csv
from config import app_config
from select_account_dialog import SelectAccountDialog
from select_currency_dialog import SelectCurrencyDialog
from transaction import Transaction
from transaction_item_model import TransactionItemModel
from ui_main_window import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.beancount_file = ''
        self.alipay_csv = ''
        self.transaction_item_model = TransactionItemModel([])
        self.setup_dialog(self.beancount_file)

    def setupUi(self):
        self.ui.setupUi(self)
        self.ui.openBeancountAccountAction.triggered.connect(self.select_beancount_file)
        self.ui.openAlipayCsvAction.triggered.connect(self.open_alipay_csv)
        self.ui.selectPaymentAccountBtn.clicked.connect(self.select_default_payment_account)
        self.ui.selectExpensesAccountBtn.clicked.connect(self.select_default_expenses_account)
        self.ui.selectCurrencyBtn.clicked.connect(self.select_default_currency)
        self.ui.transactionTableView.setModel(self.transaction_item_model)

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
            self.transaction_item_model.update_transactions_data(
                self._gen_func_set_transaction_account_with_default_value())

    def select_default_expenses_account(self):
        if self.select_account_dialog.exec() == QDialog.Accepted:
            self.ui.defaultExpensesAccountLE.setText(self.select_account_dialog.get_selected_account())
            self.transaction_item_model.update_transactions_data(
                self._gen_func_set_transaction_account_with_default_value())

    def select_default_currency(self):
        if self.select_currency_dialog.exec() == QDialog.Accepted:
            self.ui.defaultCurrencyLE.setText(self.select_currency_dialog.get_selected_currency())
            self.transaction_item_model.update_transactions_data(
                self._gen_func_set_transaction_currency_with_default_value())

    def open_alipay_csv(self):
        recent_alipay_path = path.dirname(app_config.recent_alipay_file)
        self.alipay_csv = QFileDialog.getOpenFileName(
            self, 'Open Alipay CSV file', recent_alipay_path, 'CSV (*.csv *.txt)')[0]
        app_config.recent_alipay_file = self.alipay_csv
        try:
            transactions = get_transactions_from_alipay_csv(self.alipay_csv)
            self.transaction_item_model.set_transactions_data(transactions)
            self.transaction_item_model.update_transactions_data(
                self._gen_func_set_transaction_account_with_default_value())
            self.transaction_item_model.update_transactions_data(
                self._gen_func_set_transaction_currency_with_default_value())
        except Exception as e:
            QMessageBox.critical(self, 'Failed to open Alipay csv', F'Failed to open Alipay csv: {e}')

    def _gen_func_set_transaction_account_with_default_value(self) -> Callable[[Transaction], None]:
        default_payment_account = self.ui.defaultPaymentAccountLE.text()
        default_expenses_account = self.ui.defaultExpensesAccountLE.text()

        def set_account(transaction):
            transaction.from_account = default_payment_account
            transaction.to_account = app_config.payee_account_map.get(transaction.payee, default_expenses_account)

        return set_account

    def _gen_func_set_transaction_currency_with_default_value(self) -> Callable[[Transaction], None]:
        default_currency = self.ui.defaultCurrencyLE.text()

        def set_currency(transaction):
            transaction.currency = default_currency

        return set_currency
