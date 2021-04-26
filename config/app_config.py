import os

import configparser

config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "init_files", "app.ini"))


def to_bool(bool_string):
    if bool_string == "True":
        return True
    elif bool_string == "False":
        return False
    else:
        raise SyntaxError


class AppConfig:
    def __init__(self, mode, ini_file=config_file):
        config = configparser.ConfigParser()
        config.read(ini_file)

        self.DEBUG = to_bool(config[mode]["DEBUG"])
        self.PORT = int(config[mode]["PORT"])
        self.HOST = config[mode]["HOST"]
        self.SECRET_KEY = config[mode]["SECRET_KEY"]
        self.CORS_HEADERS = config[mode]["CORS_HEADERS"]
