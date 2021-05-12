from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QHBoxLayout, QToolButton, QLineEdit, QComboBox, QDialog

from transaction_item_model import TransactionItemModelHeaderIndex
from select_account_dialog import SelectAccountDialog
from config import app_config
from typing import Callable


class TransactionViewDelegate(QStyledItemDelegate):
    ACCOUNT_LINE_EDIT = 'account_line_edit'
    ACCOUNT_SELECT_BUTTON = 'account_select_button'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.select_account_dialog = None

    def createEditor(self, parent, option, index):
        col = index.column()

        if col == TransactionItemModelHeaderIndex.CURRENCY:
            return self._create_currency_combobox_editor(parent, option, index)
        if col == TransactionItemModelHeaderIndex.FROM_ACCOUNT:
            return self._create_account_selection_editor(parent, option, index)

        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        col = index.column()

        if col == TransactionItemModelHeaderIndex.CURRENCY:
            editor.setCurrentText(index.data())
        elif col == TransactionItemModelHeaderIndex.FROM_ACCOUNT or col == TransactionItemModelHeaderIndex.TO_ACCOUNT:
            line_edit: QLineEdit = editor.findChild(QLineEdit, self.ACCOUNT_LINE_EDIT)
            if line_edit is not None:
                line_edit.setText(index.data())
                line_edit.selectAll()
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        col = index.column()
        if col == TransactionItemModelHeaderIndex.FROM_ACCOUNT or col == TransactionItemModelHeaderIndex.TO_ACCOUNT:
            line_edit: QLineEdit = editor.findChild(QLineEdit, self.ACCOUNT_LINE_EDIT)
            model.setData(index, line_edit.text())
        else:
            super().setModelData(editor, model, index)

    def _create_currency_combobox_editor(self, parent, option, index):
        combobox = QComboBox(parent)
        combobox.setEditable(True)
        for currency in app_config.beancount_currency:
            combobox.addItem(currency)

        return combobox

    def _create_account_selection_editor(self, parent, option, index):
        editor = QWidget(parent)
        layout = QHBoxLayout(editor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        line_edit = QLineEdit(editor)
        line_edit.setObjectName(self.ACCOUNT_LINE_EDIT)
        layout.addWidget(line_edit)
        button = QToolButton(editor)
        button.setText('...')
        button.setObjectName(self.ACCOUNT_SELECT_BUTTON)
        button.clicked.connect(self._select_account_action)
        layout.addWidget(button)
        editor.setLayout(layout)

        return editor

    def _select_account_action(self):
        self.select_account_dialog.open()
        #self.select_account_dialog.finished.connect()
