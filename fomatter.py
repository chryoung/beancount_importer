from transaction import Transaction


def format_amount(amount: float, precision: int = 2) -> str:
    fmt = '{:.' + str(precision) + 'f}'

    return fmt.format(amount)


def number_length_before_dot(f: float) -> int:
    s = format_amount(f)
    n = s.find('.')
    if n != -1:
        return n
    else:
        return len(s)


def format_line(account, amount, currency, absolute_neg=False, dot_pos=64) -> str:
    content = '  {0}'.format(account)
    if absolute_neg:
        amount = -1 * abs(amount)
    padding = dot_pos - len(content) - number_length_before_dot(amount)
    content += ' ' * padding
    content += format_amount(amount) + ' ' + currency

    return content


def format_transaction(transaction: Transaction) -> str:
    header = '{0} * "{1}"'.format(str(transaction.transaction_date), transaction.payee)
    if transaction.description.strip() != '':
        header += ' "{0}"'.format(transaction.description)
    to_line = format_line(transaction.to_account, transaction.amount, transaction.currency)
    from_line = format_line(transaction.from_account, transaction.amount, transaction.currency, True)

    return F'{header}\n{to_line}\n{from_line}\n'
