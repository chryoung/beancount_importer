from typing import Dict, List

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QDialog, QTableWidgetItem

from .ui_account_map_dialog import Ui_AccountMapDialog


class AccountMapDialog(QDialog):
    KEY_COLUMN = 0
    VALUE_COLUMN = 1

    finishEdit = pyqtSignal(dict, name='finishEdit')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AccountMapDialog()
        self.ui.setupUi(self)
        self.ui.addRowBtn.clicked.connect(self.add_row)
        self.ui.deleteRowBtn.clicked.connect(self.delete_row)
        self.ui.accountMapTableWidget.setColumnCount(2)

    def set_account_map(self, account_map: Dict[str, str], title: str = '', header: List[str] = None):
        if title:
            self.ui.mapTypeLabel.setText(title)
        self.ui.accountMapTableWidget.clear()
        self.ui.accountMapTableWidget.setRowCount(0)
        if header and len(header) == 2:
            header_key_item = QTableWidgetItem(header[self.KEY_COLUMN])
            value_key_item = QTableWidgetItem(header[self.VALUE_COLUMN])
            self.ui.accountMapTableWidget.setHorizontalHeaderItem(self.KEY_COLUMN, header_key_item)
            self.ui.accountMapTableWidget.setHorizontalHeaderItem(self.VALUE_COLUMN, value_key_item)
        row_count = 0
        for (k, v) in account_map.items():
            self.ui.accountMapTableWidget.insertRow(self.ui.accountMapTableWidget.rowCount())
            key_item = QTableWidgetItem(k)
            value_item = QTableWidgetItem(v)
            self.ui.accountMapTableWidget.setItem(row_count, self.KEY_COLUMN, key_item)
            self.ui.accountMapTableWidget.setItem(row_count, self.VALUE_COLUMN, value_item)
            row_count += 1

    def _save_account_map(self):
        account_map = {}
        for row_index in range(self.ui.accountMapTableWidget.rowCount()):
            key_item = self.ui.accountMapTableWidget.item(row_index, self.KEY_COLUMN)
            value_item = self.ui.accountMapTableWidget.item(row_index, self.VALUE_COLUMN)
            if key_item:
                account_map[key_item.data(Qt.ItemDataRole.DisplayRole)] = value_item.data(Qt.DisplayRole)
        self.finishEdit.emit(account_map)

    def accept(self):
        self._save_account_map()
        super().accept()

    def add_row(self):
        row_count = self.ui.accountMapTableWidget.rowCount()
        self.ui.accountMapTableWidget.insertRow(row_count)
        row_count += 1
        self.ui.accountMapTableWidget.setItem(row_count, self.KEY_COLUMN, QTableWidgetItem())
        self.ui.accountMapTableWidget.setItem(row_count, self.VALUE_COLUMN, QTableWidgetItem())

    def delete_row(self):
        indexes = self.ui.accountMapTableWidget.selectedIndexes()
        if indexes:
            index = indexes[0]
            if index.row() < self.ui.accountMapTableWidget.rowCount():
                self.ui.accountMapTableWidget.removeRow(index.row())
