import json
from os import path, mkdir


class Config:
    RECENT_BEANCOUNT_FILE = 'recent_beancount_file'
    RECENT_ALIPAY_FILE = 'recnet_alipay_file'
    RECENT_WECHAT_FILE = 'recent_wechat_file'
    DEFAULT_PAYMENT_ACCOUNT = 'default_payment_account'
    DEFAULT_EXPENSES_ACCOUNT = 'default_expenses_account'
    DEFAULT_CURRENCY = 'default_currency'
    IMPORT_TO_FILE = 'import_to_file'

    def __init__(self, config_file: str, payee_account_map_file: str):
        self._config_file = config_file
        self._config_json = self.try_load_json(self._config_file)
        self._payee_account_map_file = payee_account_map_file
        self.payee_account_map = self.try_load_json(self._payee_account_map_file)
        self.beancount_currency = []

    @staticmethod
    def try_load_json(json_file_path: str) -> {}:
        try:
            with open(json_file_path, encoding='utf-8') as fs:
                return json.load(fs)
        except:
            return {}

    def save(self):
        with open(self._config_file, 'w', encoding='utf-8') as config:
            json.dump(self._config_json, config, indent=4, ensure_ascii=False)
        with open(self._payee_account_map_file, 'w', encoding='utf-8') as payee_account_map_fs:
            json.dump(self.payee_account_map, payee_account_map_fs, indent=4, ensure_ascii=False)

    @property
    def recent_beancount_file(self):
        return self._config_json.get(self.RECENT_BEANCOUNT_FILE, '')

    @recent_beancount_file.setter
    def recent_beancount_file(self, file: str):
        if path.isfile(file):
            self._config_json[self.RECENT_BEANCOUNT_FILE] = file

    @property
    def recent_alipay_file(self):
        return self._config_json.get(self.RECENT_ALIPAY_FILE, '')

    @recent_alipay_file.setter
    def recent_alipay_file(self, file: str):
        if path.isfile(file):
            self._config_json[self.RECENT_ALIPAY_FILE] = file

    @property
    def recent_wechat_file(self):
        return self._config_json.get(self.RECENT_WECHAT_FILE, '')

    @recent_wechat_file.setter
    def recent_wechat_file(self, file: str):
        if path.isfile(file):
            self._config_json[self.RECENT_WECHAT_FILE] = file

    @property
    def default_payment_account(self):
        return self._config_json.get(self.DEFAULT_PAYMENT_ACCOUNT)

    @default_payment_account.setter
    def default_payment_account(self, value):
        self._config_json[self.DEFAULT_PAYMENT_ACCOUNT] = value

    @property
    def default_expenses_account(self):
        return self._config_json.get(self.DEFAULT_EXPENSES_ACCOUNT)

    @default_expenses_account.setter
    def default_expenses_account(self, value):
        self._config_json[self.DEFAULT_EXPENSES_ACCOUNT] = value

    @property
    def default_currency(self):
        return self._config_json.get(self.DEFAULT_CURRENCY)

    @default_currency.setter
    def default_currency(self, value):
        self._config_json[self.DEFAULT_CURRENCY] = value

    @property
    def import_to_file(self):
        return self._config_json.get(self.IMPORT_TO_FILE)

    @import_to_file.setter
    def import_to_file(self, value):
        self._config_json[self.IMPORT_TO_FILE] = value

_data_path = './data'
if not path.isdir(_data_path):
    mkdir(_data_path)

app_config = Config(F'{_data_path}/config.json', F'{_data_path}/payee_to_account.json')
