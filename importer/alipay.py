import datetime
from typing import List
from enum import IntEnum
from data_model.transaction import Transaction


class AlipayCsvFieldIndex(IntEnum):
    TRANSACTION_NO = 0
    SELLER_RECEIPT_ID = 1
    TRANSACTION_CREATION_DATETIME = 2
    PAYMENT_DATETIME = 3
    TRANSACTION_LAST_MODIFIED_DATETIME = 4
    TRANSACTION_SOURCE = 5
    TRANSACTION_TYPE = 6
    PAYEE = 7
    MERCHANDISE_NAME = 8
    AMOUNT = 9
    DIRECTION = 10
    TRANSACTION_STATE = 11
    FEE = 12
    REFUND = 13
    MEMO = 14
    CASH_STATE = 15


HEADER_LINE = 4
TRANSACTION_START_LINE = 5
TRANSACTION_END_LINE = -7

IGNORE_STATE = ['退款成功', '交易关闭', '信用服务使用成功']


def convert_line_to_transaction(transaction: List[str]) -> Transaction:
    tx = Transaction()
    transaction_date = transaction[AlipayCsvFieldIndex.PAYMENT_DATETIME]
    tx.transaction_date = datetime.datetime.strptime(transaction_date, '%Y-%m-%d %H:%M:%S').date()
    tx.payee = transaction[AlipayCsvFieldIndex.PAYEE]
    tx.description = transaction[AlipayCsvFieldIndex.MERCHANDISE_NAME]
    tx.amount = float(transaction[AlipayCsvFieldIndex.AMOUNT])

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
    return [convert_line_to_transaction(tx) for tx in transactions if tx[AlipayCsvFieldIndex.TRANSACTION_STATE] not in IGNORE_STATE]
