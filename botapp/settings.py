import os
import logging
from dotenv import load_dotenv

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Settings(metaclass=Singleton):
    def __init__(self):
        try:
            self.db_host = ''
            self.db_name = ''
            self.redis = ''
            self.api_token = ''
            self.hn_link = ''
            self.host = ''
            self.cert_file = ''
            self.cert_key = ''
            self.db_user = ''
            self.db_password = ''
            self.load_settings()

        except KeyError as exc:
            print('Environment variabe not set, loading from settings-dev.env..')

            directory = os.path.dirname(os.path.realpath(__file__))

            load_dotenv(dotenv_path=f'{directory}/settings-dev.env')
            self.load_settings()

    def load_settings(self):
        self.db_host = os.environ['DB_HOST']
        self.db_name = os.environ['DB_NAME']
        self.db_user = os.environ['DB_USER']
        self.db_password = os.environ['DB_PASSWORD']
        self.redis = os.environ['REDIS']
        self.api_token = os.environ['API_TOKEN']
        self.hn_link = os.environ['HN_LINK']
        self.host = os.environ['BOT_HOST']
        self.cert_file = os.environ.get('CERT_FILE', '')
        self.cert_key = os.environ.get('CERT_KEY', '')


class Logger(metaclass=Singleton):

    def __init__(self):
        self._logger = logging.getLogger('hn_telegram_bot')
        self._logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler() #logging.FileHandler(Settings().log)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def logger(self):
        return self._logger


settings = Settings()
