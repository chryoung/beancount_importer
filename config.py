import json
from os import path


class Config:
    RECENT_BEANCOUNT_FILE = 'recent_beancount_file'
    RECENT_ALIPAY_FILE = 'recnet_alipay_file'
    RECENT_WECHAT_FILE = 'recent_wechat_file'

    def __init__(self, config_file: str, payee_account_map_file: str):
        self._config_file = config_file
        self._config_json = self.try_load_json(self._config_file)
        self._payee_account_map_file = payee_account_map_file
        self.payee_account_map = self.try_load_json(self._payee_account_map_file)

    @staticmethod
    def try_load_json(json_file_path: str) -> {}:
        try:
            with open(json_file_path, encoding='utf-8') as fs:
                return json.load(fs)
        except:
            return {}

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

    def save(self):
        with open(self._config_file, 'w', encoding='utf-8') as config:
            json.dump(self._config_json, config)
        with open(self._payee_account_map_file, 'w', encoding='utf-8') as payee_account_map_fs:
            json.dump(self.payee_account_map, payee_account_map_fs)


app_config = Config('./data/config.json', './data/payee_to_account.json')
