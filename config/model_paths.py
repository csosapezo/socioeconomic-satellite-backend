import os

import configparser

config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "init_files", "models.ini"))


class ModelPaths:
    def __init__(self, ini_file=config_file):
        config = configparser.ConfigParser()
        config.read(ini_file)
        self.roof_model_state_dict = config["ROOF"]["STATE_DICT"]
        self.income_model_state_dict = config["INCOME"]["STATE_DICT"]
