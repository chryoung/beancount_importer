from datetime import date
from enum import IntEnum
from dataclasses import dataclass


class TransactionDirection(IntEnum):
    EXPENSES = 0
    INCOME = 1


@dataclass
class Transaction:
    will_import: bool
    transaction_date: date = date.today()
    payee: str
    description: str
    amount: float
    currency: str
    bill_payment_account: str
    direction: TransactionDirection
    from_account: str
    to_account: str
    is_modified: bool

