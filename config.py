import json
from os import path


class Config:
    RECENT_BEANCOUNT_FILE = 'recent_beancount_file'
    RECENT_ALIPAY_FILE = 'recnet_alipay_file'
    RECENT_WECHAT_FILE = 'recent_wechat_file'

    def __init__(self, config_file: str):
        self.config_file = config_file
        if path.isfile(config_file):
            try:
                with open(config_file, encoding='utf-8') as config:
                    self.config_json = json.load(config)
            except:
                self.config_json = {}

    @property
    def recent_beancount_file(self):
        return self.config_json.get(self.RECENT_BEANCOUNT_FILE, '')

    @recent_beancount_file.setter
    def recent_beancount_file(self, file: str):
        if path.isfile(file):
            self.config_json[self.RECENT_BEANCOUNT_FILE] = file

    @property
    def recent_alipay_file(self):
        return self.config_json.get(self.RECENT_ALIPAY_FILE, '')

    @recent_alipay_file.setter
    def recent_alipay_file(self, file: str):
        if path.isfile(file):
            self.config_json[self.RECENT_ALIPAY_FILE] = file

    @property
    def recent_wechat_file(self):
        return self.config_json.get(self.RECENT_WECHAT_FILE, '')

    @recent_wechat_file.setter
    def recent_wechat_file(self, file: str):
        if path.isfile(file):
            self.config_json[self.RECENT_WECHAT_FILE] = file

    def save(self):
        with open(self.config_file, 'w', encoding='utf-8') as config:
            json.dump(self.config_json, config)


app_config = Config('./data/config.json')
