from PyQt6.QtCore import QObject, pyqtSignal, QCoreApplication
import beancount.loader
from beancount.core import data


class PayeeToAccountTrainer(QObject):
    trainProgress = pyqtSignal(int, name='trainProgress')
    trainFinished = pyqtSignal(name='trainFinished')

    def __init__(self, parent=None):
        super().__init__(parent)
        self._canceled = False

    def train(self, beancount_file: str):
        (entries, error, option) = beancount.loader.load_file(beancount_file)
        transactions = [e for e in entries if type(e) == data.Transaction]
        stat = {}
        len_transactions = len(transactions)
        for tx_index in range(len_transactions):
            if self._canceled:
                break
            tx = transactions[tx_index]
            expenses_postings = [p for p in tx.postings if p.units.number > 0]
            for posting in expenses_postings:
                pair = (tx.payee, posting.account)
                if pair in stat:
                    stat[pair] += 1
                else:
                    stat[pair] = 1
            self.trainProgress.emit(tx_index / len_transactions * 0.5 * 100)
            QCoreApplication.processEvents()

        payees = list(set([p[0] for p in stat.keys() if p]))
        accounts = set([p[1] for p in stat.keys()])
        classifier = {}
        len_payees = len(payees)
        for payee_index in range(len_payees):
            if self._canceled:
                break
            payee = payees[payee_index]
            max_count = 0
            for account in accounts:
                cur_count = stat.get((payee, account), 0)
                if cur_count > max_count:
                    max_count = cur_count
                    classifier[payee] = account
            self.trainProgress.emit(((payee_index / len_payees * 0.5) + 0.5) * 100)
            QCoreApplication.processEvents()

        self.trainProgress.emit(100)
        self.trainFinished.emit()
        return classifier

    def cancel(self):
        self._canceled = True
