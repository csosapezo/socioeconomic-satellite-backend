import os

import configparser

config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "init_files", "levels.ini"))


class IncomeLevels:
    def __init__(self, ini_file=config_file, scale='LIMA'):
        config = configparser.ConfigParser()
        config.read(ini_file)
        self.levels = {}

        for index, level in config[scale].items():
            self.levels[level] = int(index)

    def __getitem__(self, level):
        return self.levels[level]
