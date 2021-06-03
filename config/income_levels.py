import os

import configparser

config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "init_files", "levels.ini"))


class IncomeLevels:
    def __init__(self, ini_file=config_file):
        config = configparser.ConfigParser()
        config.read(ini_file)
        self.levels = []

        for _, level in config["INFO"].items():
            red = int(config[level]["R"])
            green = int(config[level]["G"])
            blue = int(config[level]["B"])

            colour = (red, green, blue)
            self.levels.append(colour)

    def __getitem__(self, idx):
        return self.levels[idx]
