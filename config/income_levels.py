import os

import configparser

config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "init_files", "levels.ini"))


class IncomeLevels:
    def __init__(self, ini_file=config_file):
        config = configparser.ConfigParser()
        config.read(ini_file)
        self.levels = []
        self.labels = []

        for _, level in config["INFO"].items():
            red = int(config[level]["R"])
            green = int(config[level]["G"])
            blue = int(config[level]["B"])

            colour = (red, green, blue)
            self.levels.append(colour)
            self.labels.append(level)

    def __getitem__(self, idx):
        return self.levels[idx]

    def name(self, idx):
        return self.labels[idx]

    def __len__(self):
        return len(self.levels)
