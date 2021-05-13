from datetime import date


class Transaction:
    def __init__(self):
        self.will_import = True
        self.transaction_date = date.today()
        self.payee = ''
        self.description = ''
        self.amount = 0
        self.currency = ''
        self.from_account = ''
        self.to_account = ''
        self.is_modified = False
