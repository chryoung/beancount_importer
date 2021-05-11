import datetime
from typing import List
from transaction import Transaction

# FI = Field index
FI_TRANSACTION_NO = 0
FI_SELLER_RECEIPT_ID = 1
FI_TRANSACTION_CREATION_DATETIME = 2
FI_PAYMENT_DATETIME = 3
FI_TRANSACTION_LAST_MODIFIED_DATETIME = 4
FI_TRANSACTION_SOURCE = 5
FI_TRANSACTION_TYPE = 6
FI_PAYEE = 7
FI_MERCHANDISE_NAME = 8
FI_AMOUNT = 9
FI_DIRECTION = 10
FI_TRANSACTION_STATE = 11
FI_FEE = 12
FI_REFUND = 13
FI_MEMO = 14
FI_CASH_STATE = 15

HEADER_LINE = 4
TRANSACTION_START_LINE = 5
TRANSACTION_END_LINE = -7

IGNORE_STATE = ['退款成功', '交易关闭', '信用服务使用成功']


def convert_line_to_transaction(transaction: List[str]) -> Transaction:
    tx = Transaction()
    transaction_date = transaction[FI_PAYMENT_DATETIME]
    tx.transaction_date = datetime.datetime.strptime(transaction_date, '%Y-%m-%d %H:%M:%S').date()
    tx.payee = transaction[FI_PAYEE]
    tx.description = transaction[FI_MERCHANDISE_NAME]
    tx.amount = float(transaction[FI_AMOUNT])

    return tx


def get_transactions_from_alipay_csv(alipay_csv: str) -> List[Transaction]:
    with open(alipay_csv, encoding='gbk') as alipay_file:
        alipay_transactions = [line for line in alipay_file]

    # read transaction lines
    transactions = alipay_transactions[TRANSACTION_START_LINE:TRANSACTION_END_LINE]
    transactions = [line.split(',')[:-1] for line in transactions]
    for t_idx in range(len(transactions)):
        transactions[t_idx] = [field.strip() for field in transactions[t_idx]]

    # convert to transaction
    return [convert_line_to_transaction(tx) for tx in transactions if tx[FI_TRANSACTION_STATE] not in IGNORE_STATE]
