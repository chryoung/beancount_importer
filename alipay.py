import datetime
import pprint
import sys
import os
import json
from typing import List, Dict

alipay_journal = sys.argv[1]
if not os.path.exists(alipay_journal):
    print(F"{alipay_journal} doesn't exist!")
    exit(1)

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

FROM_ACCOUNT = 'DEFAULT'

with open('./data/payee_to_account.json') as payee_to_account_file:
    TO_ACCOUNT_DICT: Dict[str, str] = json.load(payee_to_account_file)

CURRENCY = 'CNY'


def format_amount(amount: float, precision: int=2):
    fmt = '{:.' + str(precision) + 'f}'
    return fmt.format(amount)


def number_length_before_dot(f: float):
    s = format_amount(f)
    n = s.find('.')
    if n != -1:
        return n
    else:
        return len(s)


def convert_transaction_to_beancount(transaction: List[str]):
    transaction_date = transaction[FI_PAYMENT_DATETIME]
    transaction_date = datetime.datetime.strptime(
        transaction_date, '%Y-%m-%d %H:%M:%S').date()
    payee = transaction[FI_PAYEE]
    desc = transaction[FI_MERCHANDISE_NAME]
    amount = float(transaction[FI_AMOUNT])
    to_account = TO_ACCOUNT_DICT.get(payee, 'Expenses:Other')
    return format_transaction(transaction_date, to_account, FROM_ACCOUNT, amount,
                              CURRENCY, payee, desc)


with open(alipay_journal, encoding='utf-8') as alipay_file:
    alipay_transactions = [l for l in alipay_file]

# read header
header = alipay_transactions[HEADER_LINE].split(',')[:-1]
header = [field.strip() for field in header]

# read transactions
transactions = alipay_transactions[TRANSACTION_START_LINE:TRANSACTION_END_LINE]
transactions = [line.split(',')[:-1] for line in transactions]
for t_idx in range(len(transactions)):
    transactions[t_idx] = [field.strip() for field in transactions[t_idx]]

# convert to beancount transaction
try:
    beancount_transaction = [convert_transaction_to_beancount(t) for t in transactions if t[FI_TRANSACTION_STATE] not in IGNORE_STATE]
except Exception as e:
    with open('debug_transaction.txt', 'w') as debug_out:
        pprint.pprint(transactions, debug_out)
    print('Something went wrong: ', e)
    exit(1)

# write converted file
with open('converted_from_alipay.beancount', 'w', encoding='utf-8') as output:
    for t in beancount_transaction:
        output.write(t + '\n')
