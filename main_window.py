from os import path
from typing import List, Callable

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog, QMessageBox

from alipay import get_transactions_from_alipay_csv
from config import app_config
from select_account_dialog import SelectAccountDialog
from transaction import Transaction
from transaction_item_model import TransactionItemModel
from ui_main_window import Ui_MainWindow
from transaction_view_delegate import TransactionViewDelegate
from beancount_account import get_operating_currencies, generate_account_hierarchy


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.beancount_file = ''
        self.alipay_csv = ''
        self.transaction_item_model = TransactionItemModel([])
        self.setup_beancount_option(self.beancount_file)

    def setupUi(self):
        self.ui.setupUi(self)
        self.ui.openBeancountAccountAction.triggered.connect(self.select_beancount_file)
        self.ui.openAlipayCsvAction.triggered.connect(self.open_alipay_csv)
        self.ui.selectPaymentAccountBtn.clicked.connect(self.select_default_payment_account)
        self.ui.selectExpensesAccountBtn.clicked.connect(self.select_default_expenses_account)
        self.ui.defaultCurrencyComboBox.currentTextChanged.connect(self.select_default_currency)

        # setup default value
        self.ui.defaultPaymentAccountLE.setText(app_config.default_payment_account)
        self.ui.defaultExpensesAccountLE.setText(app_config.default_expenses_account)
        self.ui.defaultCurrencyComboBox.setCurrentText(app_config.default_currency)

        # setup transaction table view
        self.ui.transactionTableView.setModel(self.transaction_item_model)
        self.ui.transactionTableView.setItemDelegate(TransactionViewDelegate(self))

    def setup_beancount_option(self, beancount_file: str):
        self.select_account_dialog = SelectAccountDialog(app_config.beancount_account, parent=self)
        self.select_account_dialog.setupUi()
        if hasattr(self.ui, 'defaultCurrencyComboBox'):
            self.ui.defaultCurrencyComboBox.clear()
            for currency in app_config.beancount_currency:
                self.ui.defaultCurrencyComboBox.addItem(currency)

    def select_beancount_file(self):
        recent_beancount_path = path.dirname(app_config.recent_beancount_file)
        self.beancount_file = QFileDialog.getOpenFileName(self, 'Open beancount file', recent_beancount_path,
                                                          'beancount (*.beancount *.bc *.txt)')[0]
        app_config.recent_beancount_file = self.beancount_file
        app_config.beancount_account = generate_account_hierarchy(self.beancount_file)
        app_config.beancount_currency = get_operating_currencies(self.beancount_file)
        self.setup_beancount_option(self.beancount_file)

    def select_default_payment_account(self):
        if self.select_account_dialog.exec() == QDialog.Accepted:
            account = self.select_account_dialog.get_selected_account()
            self.ui.defaultPaymentAccountLE.setText(account)
            app_config.default_payment_account = account
            self.transaction_item_model.update_transactions_data(
                self._gen_func_set_transaction_account_with_default_value())

    def select_default_expenses_account(self):
        if self.select_account_dialog.exec() == QDialog.Accepted:
            account = self.select_account_dialog.get_selected_account()
            self.ui.defaultExpensesAccountLE.setText(account)
            app_config.default_expenses_account = account
            self.transaction_item_model.update_transactions_data(
                self._gen_func_set_transaction_account_with_default_value())

    def select_default_currency(self, currency):
        app_config.default_currency = currency
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
        default_currency = self.ui.defaultCurrencyComboBox.currentText()

        def set_currency(transaction):
            transaction.currency = default_currency

        return set_currency
