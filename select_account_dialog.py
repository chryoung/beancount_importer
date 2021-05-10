from os import path

from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtCore import pyqtSlot, QModelIndex
from PyQt5.QtWidgets import QDialog

from ui_select_account_dialog import Ui_Dialog
from tree import Node
from beancount_account import generate_account_hierarchy

class AccountItemModel(QStandardItemModel):
    def __init__(self, account_hierarchy: Node):
        super().__init__()
        self.root_node = self.invisibleRootItem()
        self._generate_model(account_hierarchy)

    def _generate_model(self, account_hierarchy: Node):
        stack = [account_hierarchy]
        path = []
        while stack:
            account: Node = stack.pop()
            # push all children
            stack += sorted(account.children, key=lambda a: a.value, reverse=True)
            path = [account]
            # reach to root
            while account.parent is not None:
                path.append(account.parent)
                account = account.parent
            # pop root from path
            account_seg: Node = path.pop()
            # get root of the data model
            tree_model_node: QStandardItem = self.root_node
            # append the whole path to data model
            while path:
                account_seg = path.pop()
                tree_model_child: QStandardItem = None
                # find corresponding node in the data model
                for child_idx in range(tree_model_node.rowCount()):
                    child = tree_model_node.child(child_idx)
                    if child.text() == account_seg.value:
                        tree_model_child = child
                        break
                # if not found
                if tree_model_child is None:
                    # append
                    item = QStandardItem(account_seg.value)
                    item.setEditable(False)
                    tree_model_node.appendRow(item)
                    # get the child just appended and proceed
                    tree_model_node = tree_model_node.child(tree_model_node.rowCount() - 1)
                else:
                    # continue
                    tree_model_node = tree_model_child


class SelectAccountDialog(QDialog):
    def __init__(self, account_file: str, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        account_hierarchy = Node('root')
        self.account_model = AccountItemModel(account_hierarchy)
        if path.isfile(account_file):
            account_hierarchy = generate_account_hierarchy(account_file)
            self.account_model = AccountItemModel(account_hierarchy)

    def setupUi(self):
        self.ui.setupUi(self)
        self.ui.accountTreeView.setModel(self.account_model)
        self.ui.accountTreeView.setHeaderHidden(True)
        self.ui.accountTreeView.clicked.connect(self.showAccountFullName)

    def get_selection(self) -> str:
        indexes = self.ui.accountTreeView.selectedIndexes()
        if not indexes:
            return ''

        index: QModelIndex = self.ui.accountTreeView.selectedIndexes()[0]
        item: QStandardItem = self.account_model.itemFromIndex(index)
        path = []
        while item is not None:
            path.append(item.text())
            item = item.parent()

        return ':'.join(reversed(path))

    def showAccountFullName(self, index):
        self.ui.accountFullName.setText(self.get_selection())
