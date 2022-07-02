from PyQt6.QtWidgets import QStyledItemDelegate, QWidget, QHBoxLayout, QToolButton, QLineEdit, QComboBox
from PyQt6.QtCore import pyqtSlot

from data_model.transaction_item_model import TransactionItemModelHeaderIndex
from config import app_config

from .select_account_dialog import SelectAccountDialog


class LineEditWithButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.line_edit = QLineEdit(self)
        self.layout.addWidget(self.line_edit)
        self.button = QToolButton(self)
        self.button.setText('...')
        self.layout.addWidget(self.button)
        self.setFocusProxy(self.line_edit)
        self.setLayout(self.layout)

    @pyqtSlot(str, name='setLineEditText')
    def setLineEditText(self, text: str):
        self.line_edit.setText(text)


class TransactionViewDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.select_account_dialog: SelectAccountDialog

    def createEditor(self, parent, option, index):
        col = index.column()

        if col == TransactionItemModelHeaderIndex.CURRENCY:
            return self._create_currency_combobox_editor(parent, option, index)
        if col == TransactionItemModelHeaderIndex.FROM_ACCOUNT or col == TransactionItemModelHeaderIndex.TO_ACCOUNT:
            return self._create_account_selection_editor(parent, option, index)

        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        col = index.column()

        if col == TransactionItemModelHeaderIndex.CURRENCY:
            editor.setCurrentText(index.data())
        elif col == TransactionItemModelHeaderIndex.FROM_ACCOUNT or col == TransactionItemModelHeaderIndex.TO_ACCOUNT:
            editor.line_edit.setText(index.data())
            editor.line_edit.selectAll()
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        col = index.column()
        if col == TransactionItemModelHeaderIndex.FROM_ACCOUNT or col == TransactionItemModelHeaderIndex.TO_ACCOUNT:
            model.setData(index, editor.line_edit.text())
        else:
            super().setModelData(editor, model, index)

    def _create_currency_combobox_editor(self, parent, option, index):
        combobox = QComboBox(parent)
        combobox.setEditable(True)
        for currency in app_config.beancount_currency:
            combobox.addItem(currency)

        return combobox

    def _create_account_selection_editor(self, parent, option, index):
        editor = LineEditWithButton(parent)
        editor.button.clicked.connect(self.select_account_dialog.open)
        self.select_account_dialog.selectedAccount.connect(editor.setLineEditText)

        return editor
