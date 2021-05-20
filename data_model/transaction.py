from datetime import date
from enum import IntEnum


class TransactionDirection(IntEnum):
    EXPENSES = 0
    INCOME = 1


class Transaction:
    def __init__(self):
        self.will_import = True
        self.transaction_date = date.today()
        self.payee = ''
        self.description = ''
        self.amount = 0
        self.currency = ''
        self.bill_payment_account = ''
        self.direction = TransactionDirection.EXPENSES
        self.from_account = ''
        self.to_account = ''
        self.is_modified = False
