import logging
import os
from os import path
from typing import Callable
import traceback

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog, QMessageBox, QLineEdit, QProgressDialog
from PyQt5.QtGui import QIcon

from importer.alipay import get_transactions_from_alipay_csv
from importer.wechat import get_transactions_from_wechat_csv
from config import app_config
from data_model.transaction import Transaction
from data_model.transaction_item_model import TransactionItemModel
from gui.ui_main_window import Ui_MainWindow
from gui.transaction_view_delegate import TransactionViewDelegate
from beancount_account import get_operating_currencies, generate_account_hierarchy
from fmt import format_transaction
from data_model.tree import Node
from trainer.payee_to_account_trainer import PayeeToAccountTrainer

from .select_account_dialog import SelectAccountDialog
from .account_map_dialog import AccountMapDialog


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.alipay_csv = ''
        self.transaction_item_model = TransactionItemModel([])
        self.transaction_view_delegate = TransactionViewDelegate(self)
        self._account_map_dialog = AccountMapDialog(self)

    def setupUi(self):
        self.ui.setupUi(self)

        # setup file menu action trigger
        self.ui.openBeancountAccountAction.triggered.connect(self.select_beancount_file)
        self.ui.openAlipayCsvAction.triggered.connect(self.open_alipay_csv)
        self.ui.openWechatCsvAction.triggered.connect(self.open_wechat_csv)

        # setup account map menu action
        self.ui.payeeToAccountAction.triggered.connect(self.edit_payee_to_account)
        self.ui.billAccountToFromAccountAction.triggered.connect(self.edit_bill_account_to_from_account)
        self.ui.trainPayeeToAccountMapAction.triggered.connect(self.train_payee_to_account)

        # setup default value button and line edit
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
        try:
            accounts = generate_account_hierarchy(beancount_file)
            app_config.beancount_currency = get_operating_currencies(beancount_file)
        except Exception as e:
            trace = traceback.format_exc()
            logging.error('Failed to load beancount file: {0}\n{1}'.format(e, trace))

            accounts = Node('root')
            app_config.beancount_currency = []
            QMessageBox.critical(self, self.tr('Error'), self.tr('Failed to load beancount file: {0}\n{1}').format(e, trace))
        self.select_account_dialog = SelectAccountDialog(accounts, parent=self)
        self.select_account_dialog.setupUi()
        self.transaction_view_delegate.select_account_dialog = self.select_account_dialog
        self.ui.defaultCurrencyComboBox.clear()
        for currency in app_config.beancount_currency:
            self.ui.defaultCurrencyComboBox.addItem(currency)

    def select_beancount_file(self):
        logging.debug('Select beancount file.')
        recent_beancount_path = path.dirname(app_config.recent_beancount_file)
        app_config.recent_beancount_file = QFileDialog.getOpenFileName(self, self.tr('Open beancount file'), recent_beancount_path,
                                                                       'beancount (*.beancount *.bc *.txt)')[0]
        if not os.path.isfile(app_config.recent_beancount_file):
            return
        self.setup_beancount_option(app_config.recent_beancount_file)

    def set_default_payment_account(self, account):
        logging.debug('Set default payment account.')
        self.ui.defaultPaymentAccountLE.setText(account)
        app_config.default_payment_account = account
        self.transaction_item_model.update_transactions_data(
            self._gen_func_set_transaction_account_with_default_value())

    def select_default_payment_account(self):
        logging.debug('Select default payment account.')
        if self.select_account_dialog.exec() == QDialog.Accepted:
            account = self.select_account_dialog.get_selected_account()
            self.set_default_payment_account(account)

    def set_default_expenses_account(self, account):
        logging.debug('Set default expenses account.')
        self.ui.defaultExpensesAccountLE.setText(account)
        app_config.default_expenses_account = account
        self.transaction_item_model.update_transactions_data(
            self._gen_func_set_transaction_account_with_default_value())

    def select_default_expenses_account(self):
        logging.debug('Select default expenses account.')
        if self.select_account_dialog.exec() == QDialog.Accepted:
            account = self.select_account_dialog.get_selected_account()
            self.set_default_expenses_account(account)

    def set_default_currency(self, currency):
        logging.debug('Set default currency.')
        app_config.default_currency = currency
        self.transaction_item_model.update_transactions_data(
            self._gen_func_set_transaction_currency_with_default_value())

    def open_alipay_csv(self):
        logging.debug('Open Alipay CSV.')
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
            trace = traceback.format_exc()
            logging.error('Failed to open Alipay csv: {0}\n{1}'.format(e, trace))
            QMessageBox.critical(self, self.tr('Failed to open Alipay csv'), self.tr('Failed to open Alipay csv: ') + '{0}\n{1}'.format(e, trace))

    def open_wechat_csv(self):
        logging.debug('Open Wechat CSV.')
        recent_wechat_path = path.dirname(app_config.recent_wechat_file)
        self.wechat_csv = QFileDialog.getOpenFileName(
            self, self.tr('Open Wechat CSV file'), recent_wechat_path, 'CSV (*.csv *.txt)')[0]
        if not os.path.isfile(self.wechat_csv):
            return
        app_config.recent_wechat_file = self.wechat_csv
        try:
            transactions = get_transactions_from_wechat_csv(self.wechat_csv)
            self.transaction_item_model.set_transactions_data(transactions)
            self.transaction_item_model.update_transactions_data(
                self._gen_func_set_transaction_account_with_default_value())
            self.transaction_item_model.update_transactions_data(
                self._gen_func_set_transaction_currency_with_default_value())
        except Exception as e:
            trace = traceback.format_exc()
            logging.error('Failed to open Wechat csv: {0}\n{1}'.format(e, trace))
            QMessageBox.critical(self, self.tr('Failed to open Wechat csv'), self.tr('Failed to open Wechat csv: ') + '{0}\n{1}'.format(e, trace))

    def select_import_file(self):
        logging.debug('Select import file.')
        import_file = QFileDialog.getSaveFileName(self, self.tr('Import to'), '/', 'beancount (*.beancount *.txt)')
        if import_file[0]:
            self.ui.importToPathLE.setText(import_file[0])
            app_config.import_to_file = import_file[0]

    def _gen_func_set_transaction_account_with_default_value(self) -> Callable[[Transaction], None]:
        default_payment_account = self.ui.defaultPaymentAccountLE.text()
        default_expenses_account = self.ui.defaultExpensesAccountLE.text()

        def set_account(transaction):
            transaction.from_account = app_config.bill_account_to_from_account.get(transaction.bill_payment_account, default_payment_account)
            transaction.to_account = app_config.payee_account_map.get(transaction.payee, default_expenses_account)

        return set_account

    def _gen_func_set_transaction_currency_with_default_value(self) -> Callable[[Transaction], None]:
        default_currency = self.ui.defaultCurrencyComboBox.currentText()

        def set_currency(transaction):
            transaction.currency = default_currency

        return set_currency

    def import_transaction(self):
        logging.debug('Import transaction.')
        import_file = self.ui.importToPathLE.text()
        if not import_file:
            QMessageBox.warning(self, self.tr('Import path is not set!'), self.tr('Import path is not set! Please set an import path first.'))
            return

        transaction_text_lines = [format_transaction(tx) for tx in self.transaction_item_model.transactions if tx.will_import]
        transactions_text = '\n'.join(transaction_text_lines)
        try:
            with open(import_file, 'a', encoding='utf-8') as import_file_fs:
                import_file_fs.write(transactions_text)
            QMessageBox.debugrmation(self, self.tr('Imported'), self.tr('Imported {0} transactions').format(len(transaction_text_lines)))
        except IOError as e:
            trace = traceback.format_exc()
            logging.error('Cannot import transactions: {0}\n{1}'.format(e, trace))
            QMessageBox.critical(self, self.tr('Cannot import transactions'), self.tr('Cannot import transactions: ') + '{0}\n{1}'.format(e, trace))

    def set_payee_to_account(self, value):
        logging.debug('Set payee to account.')
        app_config.payee_account_map = value

    def set_bill_account_to_from_account(self, value):
        logging.debug('Set bill "Account to" from account.')
        app_config.bill_account_to_from_account = value

    def edit_payee_to_account(self):
        logging.debug('Edit "Payee to" account')
        self._account_map_dialog.set_account_map(app_config.payee_account_map, self.tr('Payee to account'), [self.tr('Payee'), self.tr('Account')])
        try:
            self._account_map_dialog.finishEdit.disconnect()
        except:
            pass
        self._account_map_dialog.finishEdit.connect(self.set_payee_to_account)
        self._account_map_dialog.open()

    def edit_bill_account_to_from_account(self):
        logging.debug('Edit bill "account to" from account.')
        self._account_map_dialog.set_account_map(app_config.bill_account_to_from_account, self.tr('Bill account to From account'), [self.tr('Bill account'), self.tr('From account')])
        try:
            self._account_map_dialog.finishEdit.disconnect()
        except:
            pass
        self._account_map_dialog.finishEdit.connect(self.set_bill_account_to_from_account)
        self._account_map_dialog.open()

    def train_payee_to_account(self):
        logging.debug("Train payee to account.")
        if not os.path.isfile(app_config.recent_beancount_file):
            QMessageBox.critical(self, self.tr('Error'), self.tr('No beancount file is open for traning.'))
            return
        dialog = QProgressDialog(self.tr('Training...'), self.tr('Abort training'), 0, 100, self)
        trainer = PayeeToAccountTrainer(self)
        trainer.trainProgress.connect(dialog.setValue)
        dialog.canceled.connect(trainer.cancel)
        dialog.open()
        try:
            result = trainer.train(app_config.recent_beancount_file)
            for (payee, account) in result.items():
                if payee in app_config.payee_account_map and app_config.payee_account_map[payee] != account:
                    overwrite = QMessageBox.question(self,
                                                     self.tr('Overwrite?'),
                                                     self.tr('{0} already exists on payee to account map with value {1}. Do you want to overwite it with {2}?').format(payee, app_config.payee_account_map[payee], account))
                    if overwrite == QMessageBox.Yes:
                        app_config.payee_account_map[payee] = account
                else:
                    app_config.payee_account_map[payee] = account
        except Exception as e:
            trace = traceback.format_exc()
            logging.error('An error occurred while training: {0}\n{1}'.format(e, trace))
            QMessageBox.critical(self, self.tr('Error'), self.tr('An error occurred while training: {0}\n{1}').format(e, trace))
            dialog.close()
