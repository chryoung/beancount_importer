from os import path

from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QDialog

from tree import Node
from ui_select_account_dialog import Ui_Dialog


class AccountItemModel(QStandardItemModel):
    def __init__(self, account_hierarchy: Node):
        super().__init__()
        self.root_node = self.invisibleRootItem()
        self._generate_model(account_hierarchy)

    def _generate_model(self, account_hierarchy: Node):
        stack = [account_hierarchy]
        while stack:
            account: Node = stack.pop()
            # push all children
            stack += sorted(account.children, key=lambda a: a.value, reverse=True)
            path_of_account = [account]
            # reach to root
            while account.parent is not None:
                path_of_account.append(account.parent)
                account = account.parent
            # pop root from path
            account_seg: Node = path_of_account.pop()
            # get root of the data model
            tree_model_node: QStandardItem = self.root_node
            # append the whole path to data model
            while path_of_account:
                account_seg = path_of_account.pop()
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
    def __init__(self, account_hierarchy: Node, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.account_model = AccountItemModel(account_hierarchy)

    def setupUi(self):
        self.ui.setupUi(self)
        self.ui.accountTreeView.setModel(self.account_model)
        self.ui.accountTreeView.setHeaderHidden(True)
        self.ui.accountTreeView.clicked.connect(self.show_account_full_name)

    def get_selected_account(self) -> str:
        indexes = self.ui.accountTreeView.selectedIndexes()
        if not indexes:
            return ''

        index: QModelIndex = self.ui.accountTreeView.selectedIndexes()[0]
        item: QStandardItem = self.account_model.itemFromIndex(index)
        path_of_item = []
        while item is not None:
            path_of_item.append(item.text())
            item = item.parent()

        return ':'.join(reversed(path_of_item))

    def show_account_full_name(self, index):
        self.ui.accountFullName.setText(self.get_selected_account())
