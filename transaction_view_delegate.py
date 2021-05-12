from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QHBoxLayout, QToolButton, QLineEdit

from transaction_item_model import TransactionItemModelHeaderIndex


class TransactionViewDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        return super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        return super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor, option, index):
        return super().updateEditorGeometry(editor, option, index)
