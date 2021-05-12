import datetime
from typing import List
from enum import IntEnum

from data_model.transaction import Transaction


class WechatCsvFieldIndex(IntEnum):
    TRANSACTION_DATETIME = 0
    TRANSACTION_TYPE = 1
    PAYEE = 2
    MERCHANDISE_NAME = 3
    DIRECTION = 4
    AMOUNT = 5
    PAYMENT_ACCOUNT = 6
    TRANSACTION_STATE = 7
    TRANSACTION_NO = 8
    SELLER_RECEIPT_ID = 9
    MEMO = 10

HEADER_LINE = 16
TRANSACTION_START_LINE = 17
TRANSACTION_END_LINE = -1

def convert_line_to_transaction(transaction: List[str]) -> Transaction:
    tx = Transaction()
    transaction_date = transaction[WechatCsvFieldIndex.TRANSACTION_DATETIME]
    tx.transaction_date = datetime.datetime.strptime(transaction_date, '%Y-%m-%d %H:%M:%S').date()
    tx.payee = transaction[WechatCsvFieldIndex.PAYEE]
    tx.description = transaction[WechatCsvFieldIndex.MERCHANDISE_NAME]
    tx.amount = float(transaction[WechatCsvFieldIndex.AMOUNT][1:])

    return tx


def get_transactions_from_wechat_csv(wechat_csv: str) -> List[Transaction]:
    with open(wechat_csv, encoding='utf-8') as wechat_file:
        wechat_transactions = [line for line in wechat_file]

    # read transaction lines
    transactions = wechat_transactions[TRANSACTION_START_LINE:TRANSACTION_END_LINE]
    transactions = [line.split(',')[:-1] for line in transactions]
    for t_idx in range(len(transactions)):
        transactions[t_idx] = [field.strip() for field in transactions[t_idx]]

    # convert to transaction
    return [convert_line_to_transaction(tx) for tx in transactions]
