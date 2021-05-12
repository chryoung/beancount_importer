import os
from os import path
from typing import Callable

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog, QMessageBox, QLineEdit
from PyQt5.QtGui import QIcon

from importer.alipay import get_transactions_from_alipay_csv
from config import app_config
from .select_account_dialog import SelectAccountDialog
from data_model.transaction import Transaction
from data_model.transaction_item_model import TransactionItemModel
from gui.ui_main_window import Ui_MainWindow
from gui.transaction_view_delegate import TransactionViewDelegate
from beancount_account import get_operating_currencies, generate_account_hierarchy
from fmt import format_transaction


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.alipay_csv = ''
        self.transaction_item_model = TransactionItemModel([])
        self.transaction_view_delegate = TransactionViewDelegate(self)

    def setupUi(self):
        self.ui.setupUi(self)
        self.ui.openBeancountAccountAction.triggered.connect(self.select_beancount_file)
        self.ui.openAlipayCsvAction.triggered.connect(self.open_alipay_csv)
        self.ui.selectPaymentAccountBtn.clicked.connect(self.select_default_payment_account)
        self.ui.selectExpensesAccountBtn.clicked.connect(self.select_default_expenses_account)
        self.ui.defaultCurrencyComboBox.currentTextChanged.connect(self.set_default_currency)
        self.ui.defaultPaymentAccountLE.textChanged.connect(self.set_default_payment_account)
        self.ui.defaultExpensesAccountLE.textChanged.connect(self.set_default_expenses_account)

        # setup default value
        self.ui.defaultPaymentAccountLE.setText(app_config.default_payment_account)
        self.ui.defaultExpensesAccountLE.setText(app_config.default_expenses_account)
        self.ui.defaultCurrencyComboBox.setCurrentText(app_config.default_currency)

        # setup transaction table view
        self.ui.transactionTableView.setModel(self.transaction_item_model)
        self.ui.transactionTableView.setItemDelegate(self.transaction_view_delegate)

        # setup import component
        open_file_icon = QIcon('./resources/icon/folder-open-line.svg')
        self.ui.importToPathLE.setText(app_config.import_to_file)
        importToPathLE_action = self.ui.importToPathLE.addAction(open_file_icon, QLineEdit.ActionPosition.TrailingPosition)
        importToPathLE_action.triggered.connect(self.select_import_file)
        self.ui.importBtn.clicked.connect(self.import_transaction)

    def setup_beancount_option(self, beancount_file: str):
        accounts = generate_account_hierarchy(beancount_file)
        self.select_account_dialog = SelectAccountDialog(accounts, parent=self)
        self.select_account_dialog.setupUi()
        self.transaction_view_delegate.select_account_dialog = self.select_account_dialog
        app_config.beancount_currency = get_operating_currencies(beancount_file)
        if hasattr(self.ui, 'defaultCurrencyComboBox'):
            self.ui.defaultCurrencyComboBox.clear()
            for currency in app_config.beancount_currency:
                self.ui.defaultCurrencyComboBox.addItem(currency)

    def select_beancount_file(self):
        recent_beancount_path = path.dirname(app_config.recent_beancount_file)
        app_config.recent_beancount_file = QFileDialog.getOpenFileName(self, self.tr('Open beancount file'), recent_beancount_path,
                                                                       'beancount (*.beancount *.bc *.txt)')[0]
        if not os.path.isfile(app_config.recent_beancount_file):
            return
        self.setup_beancount_option(app_config.recent_beancount_file)

    def set_default_payment_account(self, account):
        self.ui.defaultPaymentAccountLE.setText(account)
        app_config.default_payment_account = account
        self.transaction_item_model.update_transactions_data(
            self._gen_func_set_transaction_account_with_default_value())

    def select_default_payment_account(self):
        if self.select_account_dialog.exec() == QDialog.Accepted:
            account = self.select_account_dialog.get_selected_account()
            self.set_default_payment_account(account)

    def set_default_expenses_account(self, account):
        self.ui.defaultExpensesAccountLE.setText(account)
        app_config.default_expenses_account = account
        self.transaction_item_model.update_transactions_data(
            self._gen_func_set_transaction_account_with_default_value())

    def select_default_expenses_account(self):
        if self.select_account_dialog.exec() == QDialog.Accepted:
            account = self.select_account_dialog.get_selected_account()
            self.set_default_expenses_account(account)

    def set_default_currency(self, currency):
        app_config.default_currency = currency
        self.transaction_item_model.update_transactions_data(
            self._gen_func_set_transaction_currency_with_default_value())

    def open_alipay_csv(self):
        recent_alipay_path = path.dirname(app_config.recent_alipay_file)
        self.alipay_csv = QFileDialog.getOpenFileName(
            self, self.tr('Open Alipay CSV file'), recent_alipay_path, 'CSV (*.csv *.txt)')[0]
        if not os.path.isfile(self.alipay_csv):
            return
        app_config.recent_alipay_file = self.alipay_csv
        try:
            transactions = get_transactions_from_alipay_csv(self.alipay_csv)
            self.transaction_item_model.set_transactions_data(transactions)
            self.transaction_item_model.update_transactions_data(
                self._gen_func_set_transaction_account_with_default_value())
            self.transaction_item_model.update_transactions_data(
                self._gen_func_set_transaction_currency_with_default_value())
        except Exception as e:
            QMessageBox.critical(self, self.tr('Failed to open Alipay csv'), self.tr('Failed to open Alipay csv: ') + str(e))

    def select_import_file(self):
        import_file = QFileDialog.getSaveFileName(self, self.tr('Import to'), '/', 'beancount (*.beancount *.txt)')
        if import_file[0]:
            self.ui.importToPathLE.setText(import_file[0])
            app_config.import_to_file = import_file[0]

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

    def import_transaction(self):
        import_file = self.ui.importToPathLE.text()
        if not import_file:
            QMessageBox.warning(self, self.tr('Import path is not set!'), self.tr('Import path is not set! Please set an import path first.'))
            return

        transaction_text_lines = [format_transaction(tx) for tx in self.transaction_item_model.transactions if tx.will_import]
        transactions_text = '\n'.join(transaction_text_lines)
        try:
            with open(import_file, 'a', encoding='utf-8') as import_file_fs:
                import_file_fs.write(transactions_text)
            QMessageBox.information(self, self.tr('Imported'), self.tr('Imported {0} transactions').format(len(transaction_text_lines)))
        except IOError as e:
            QMessageBox.critical(self, self.tr('Cannot import transactions'), self.tr('Cannot import transactions: ') + str(e))
