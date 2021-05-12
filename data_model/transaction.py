from datetime import date
from dataclasses import dataclass


@dataclass(init=False)
class Transaction:
    will_export: bool
    transaction_date: date
    payee: str
    description: str
    amount: float
    currency: str
    from_account: str
    to_account: str
    is_modified: bool

    def __init__(self):
        self.will_export = True
        self.transaction_date = date.today()
        self.payee = ''
        self.description = ''
        self.amount = 0
        self.currency = ''
        self.from_account = ''
        self.to_account = ''
        self.is_modified = False
