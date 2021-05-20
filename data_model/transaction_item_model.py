from typing import List, Callable
from enum import IntEnum
import datetime

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QCoreApplication

from .transaction import Transaction, TransactionDirection

tr = QCoreApplication.translate


class TransactionItemModelHeaderIndex(IntEnum):
    IMPORT = 0
    TRANSACTION_DATE = 1
    AMOUNT = 2
    CURRENCY = 3
    FROM_ACCOUNT = 4
    TO_ACCOUNT = 5
    PAYEE = 6
    DESCRIPTION = 7
    DIRECTION = 8
    END = 9


class TransactionItemModel(QAbstractTableModel):
    HEADERS = [
        tr('TransactionItemModel', 'Import'),
        tr('TransactionItemModel', 'Transaction date'),
        tr('TransactionItemModel', 'Amount'),
        tr('TransactionItemModel', 'Currency'),
        tr('TransactionItemModel', 'From account'),
        tr('TransactionItemModel', 'To account'),
        tr('TransactionItemModel', 'Payee'),
        tr('TransactionItemModel', 'Description'),
        tr('TransactionItemModel', 'Direction'),
    ]

    def __init__(self, transactions: List[Transaction]):
        super().__init__()
        self.transactions = transactions

    def columnCount(self, parent=None) -> int:
        return TransactionItemModelHeaderIndex.END

    def rowCount(self, parent=None) -> int:
        return len(self.transactions)

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < TransactionItemModelHeaderIndex.END:
                    return self.HEADERS[section]
            elif orientation == Qt.Vertical:
                return section + 1

        return None

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        row = index.row()
        col = index.column()

        if row >= len(self.transactions) or col >= TransactionItemModelHeaderIndex.END:
            return None

        transaction = self.transactions[row]

        if role == Qt.CheckStateRole and col == TransactionItemModelHeaderIndex.IMPORT:
            return Qt.Checked if transaction.will_import else Qt.Unchecked
        elif role == Qt.DisplayRole or role == Qt.EditRole:
            if col == TransactionItemModelHeaderIndex.TRANSACTION_DATE:
                return str(transaction.transaction_date)
            elif col == TransactionItemModelHeaderIndex.AMOUNT:
                return transaction.amount
            elif col == TransactionItemModelHeaderIndex.CURRENCY:
                return transaction.currency
            elif col == TransactionItemModelHeaderIndex.FROM_ACCOUNT:
                return transaction.from_account
            elif col == TransactionItemModelHeaderIndex.TO_ACCOUNT:
                return transaction.to_account
            elif col == TransactionItemModelHeaderIndex.PAYEE:
                return transaction.payee
            elif col == TransactionItemModelHeaderIndex.DESCRIPTION:
                return transaction.description
            elif col == TransactionItemModelHeaderIndex.DIRECTION:
                return 'Expenses' if transaction.direction == TransactionDirection.EXPENSES else 'Income'

        return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        row = index.row()
        col = index.column()

        if row >= len(self.transactions) or col >= TransactionItemModelHeaderIndex.END:
            return False

        if role == Qt.CheckStateRole and col == TransactionItemModelHeaderIndex.IMPORT:
            self.transactions[row].will_import = (value == Qt.Checked)
            return True
        elif role == Qt.EditRole:
            if col == TransactionItemModelHeaderIndex.AMOUNT:
                self.transactions[row].amount = value
                return True
            elif col == TransactionItemModelHeaderIndex.TRANSACTION_DATE:
                try:
                    transaction_date = datetime.datetime.strptime(value, '%Y-%m-%d').date()
                    self.transactions[row].transaction_date = transaction_date
                    return True
                except:
                    return False
            elif col == TransactionItemModelHeaderIndex.CURRENCY:
                self.transactions[row].is_modified = (self.transactions[row].is_modified or (self.transactions[row].currency != value))
                self.transactions[row].currency = value
                return True
            elif col == TransactionItemModelHeaderIndex.FROM_ACCOUNT:
                self.transactions[row].is_modified = (self.transactions[row].is_modified or (self.transactions[row].from_account != value))
                self.transactions[row].from_account = value
                return True
            elif col == TransactionItemModelHeaderIndex.TO_ACCOUNT:
                self.transactions[row].is_modified = (self.transactions[row].is_modified or (self.transactions[row].to_account != value))
                self.transactions[row].to_account = value
                return True
            elif col == TransactionItemModelHeaderIndex.PAYEE:
                self.transactions[row].payee = value
                return True
            elif col == TransactionItemModelHeaderIndex.DESCRIPTION:
                self.transactions[row].description = value
                return True

        return False

    def flags(self, index):
        if index.column() == TransactionItemModelHeaderIndex.IMPORT:
            return super().flags(index) | Qt.ItemIsUserCheckable
        elif index.column() != TransactionItemModelHeaderIndex.DIRECTION:
            return super().flags(index) | Qt.ItemIsEditable
        else:
            return super().flags(index)

    def set_transactions_data(self, transactions: List[Transaction]):
        self.layoutAboutToBeChanged.emit()
        self.transactions = transactions
        self.layoutChanged.emit()

    def update_transactions_data(self, update_func: Callable[[Transaction], None]):
        self.layoutAboutToBeChanged.emit()
        for tx in self.transactions:
            if tx.is_modified:
                continue
            update_func(tx)
        self.layoutChanged.emit()
