def format_line(account, amount, currency, absolute_neg=False, dot_pos=64):
    content = '  {0}'.format(account)
    if absolute_neg:
        amount = -1 * abs(amount)
    padding = dot_pos - len(content) - number_length_before_dot(amount)
    content += ' ' * padding
    content += format_amount(amount) + ' ' + currency
    return content


def format_transaction(posting_date, to_account, from_account, amount,
                       posting_currency, payee, description):
    header = '{0} * "{1}"'.format(str(posting_date), payee)
    if description.strip() != '':
        header += ' "{0}"'.format(description)
    to_line = format_line(to_account, amount, posting_currency)
    from_line = format_line(from_account, amount, posting_currency, True)

    return F'{header}\n{to_line}\n{from_line}\n'
