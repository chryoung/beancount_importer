import datetime
import logging
from enum import IntEnum

from data_model.transaction import Transaction, TransactionDirection

HEADER_LINE = 16
TRANSACTION_START_LINE = 17
TRANSACTION_END_LINE = -1


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


def convert_line_to_transaction(line_number: int, transaction: list[str]) -> Transaction:
    tx = Transaction()

    # Get transaction date
    transaction_date = transaction[WechatCsvFieldIndex.TRANSACTION_DATETIME]
    tx.transaction_date = datetime.datetime.strptime(transaction_date, '%Y-%m-%d %H:%M:%S').date()

    # Get payee
    tx.payee = transaction[WechatCsvFieldIndex.PAYEE]

    # Get description
    tx.description = transaction[WechatCsvFieldIndex.MERCHANDISE_NAME][1:-2]

    # Get amount
    try:
        if transaction[WechatCsvFieldIndex.AMOUNT].startswith('¥'):
            tx.amount = float(transaction[WechatCsvFieldIndex.AMOUNT][1:])
        else:
            tx.amount = float(transaction[WechatCsvFieldIndex.AMOUNT])
    except ValueError as ve:
        logging.error('Line {0}: failed to convert amount from {1} to float: {2}'.format(line_number, transaction[WechatCsvFieldIndex.AMOUNT], ve))
        tx.amount = 0.0

    # Get bill payment account
    tx.bill_payment_account = transaction[WechatCsvFieldIndex.PAYMENT_ACCOUNT]

    # Get transaction direction
    tx.direction = TransactionDirection.EXPENSES if transaction[WechatCsvFieldIndex.DIRECTION] == '支出' else TransactionDirection.INCOME

    return tx


def get_transactions_from_wechat_csv(wechat_csv: str) -> list[Transaction]:
    logging.debug('Get transactions from Wechat CSV.')
    with open(wechat_csv, encoding='utf-8') as wechat_file:
        wechat_transactions = [(no + 1, line) for no, line in enumerate(wechat_file)]

    # read transaction lines
    transactions = wechat_transactions[TRANSACTION_START_LINE:TRANSACTION_END_LINE]
    transactions = [(line_number, line.split(',')[:-1]) for line_number, line in transactions]
    for t_idx in range(len(transactions)):
        transactions[t_idx] = (transactions[t_idx][0], [field.strip() for field in transactions[t_idx][1]])

    # convert to transaction
    logging.debug(F'Number of transactions: {len(transactions)}.')
    return [convert_line_to_transaction(line_number, tx) for line_number, tx in transactions]
