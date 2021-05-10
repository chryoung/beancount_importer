from os import path
from PyQt5.Qt import QStringListModel
from PyQt5.QtWidgets import QDialog, QAbstractItemView

from ui_select_currency_dialog import Ui_Dialog
from beancount_account import get_operating_currencies


class SelectCurrencyDialog(QDialog):
    def __init__(self, beancount_file, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.currencies = get_operating_currencies(beancount_file) if path.isfile(beancount_file) else []
        self.currencies_model = QStringListModel()
        self.currencies_model.setStringList(self.currencies)

    def setupUi(self):
        self.ui.setupUi(self)
        self.ui.currencyListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.currencyListView.setModel(self.currencies_model)

    def get_selected_currency(self) -> str:
        indexes = self.ui.currencyListView.selectedIndexes()
        if not indexes:
            return ''

        return self.currencies[indexes[0].row()]
