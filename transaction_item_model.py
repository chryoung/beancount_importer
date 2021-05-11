from typing import List, Callable

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex

from transaction import Transaction


class TransactionItemModel(QAbstractTableModel):
    NUM_COLUMNS = 8
    HEADERS = [
        'Import',
        'Transaction date',
        'Amount',
        'Currency',
        'From account',
        'To account',
        'Payee',
        'Description',
    ]

    def __init__(self, transactions: List[Transaction]):
        super().__init__()
        self.transactions = transactions

    def columnCount(self, parent=None) -> int:
        return self.NUM_COLUMNS

    def rowCount(self, parent=None) -> int:
        return len(self.transactions)

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section <= len(self.HEADERS):
                    return self.HEADERS[section]

        return None

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        row = index.row()
        col = index.column()

        if row > len(self.transactions):
            return None

        if col > len(self.HEADERS):
            return None

        transaction = self.transactions[row]

        if role == Qt.CheckStateRole and col == 0:
            return Qt.Checked if transaction.will_import else Qt.Unchecked

        if role == Qt.DisplayRole:
            if col == 1:
                return str(transaction.transaction_date)
            elif col == 2:
                return transaction.amount
            elif col == 3:
                return transaction.currency
            elif col == 4:
                return transaction.from_account
            elif col == 5:
                return transaction.to_account
            elif col == 6:
                return transaction.payee
            elif col == 7:
                return transaction.description

        return None

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
