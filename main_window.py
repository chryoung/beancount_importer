from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog

from ui_main_window import Ui_MainWindow
from select_account_dialog import SelectAccountDialog

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.beancount_file = ''
        self.setup_select_account_dialog(self.beancount_file)

    def setupUi(self):
        self.ui.setupUi(self)
        self.ui.openBeancountAccountAction.triggered.connect(self.select_account_file)
        self.ui.selectPaymentAccountBtn.clicked.connect(self.select_default_payment_account)

    def setup_select_account_dialog(self, beancount_file: str):
        self.select_account_dialog = SelectAccountDialog(beancount_file, parent=self)
        self.select_account_dialog.setupUi()

    def select_account_file(self):
        self.beancount_file = QFileDialog.getOpenFileName(self, 'Open beancount file', '/', 'beancount (*.beancount *.bc *.txt)')[0]
        self.setup_select_account_dialog(self.beancount_file)

    def select_default_payment_account(self):
        result = self.select_account_dialog.exec()
        if result == QDialog.Accepted:
            self.ui.defaultPaymentAccountLE.setText(self.select_account_dialog.get_selection())
