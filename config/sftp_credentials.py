import os

import configparser

config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "init_files", "sftp.ini"))


class SFTPCredentials:
    def __init__(self, ini_file=config_file):
        config = configparser.ConfigParser()
        print(ini_file)
        config.read(ini_file)
        print(config)
        self.sftp_hostname = config["SFTP"]["HOSTNAME"]
        self.sftp_username = config["SFTP"]["USERNAME"]
        self.sftp_password = config["SFTP"]["PASSWORD"]
