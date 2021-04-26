import os

import configparser

import config
from config.sftp_credentials import SFTPCredentials

config_file = os.path.abspath(os.path.join(os.path.dirname(config.sftp_credentials.__file__), "init_files"))


def creat_mock_ini_file():
    mock = configparser.ConfigParser()
    mock["SFTP"] = {
        'HOSTNAME': '0.0.0.0',
        'USERNAME': 'testuser',
        'PASSWORD': 'testpassword'
    }

    with open(str(os.path.join(config_file, "test_sftp.ini")), 'w') as configfile:
        mock.write(configfile)


def test_hostname_is_read():
    creat_mock_ini_file()
    test_config = SFTPCredentials(str(os.path.join(config_file, "test_sftp.ini")))
    os.remove(str(os.path.join(config_file, "test_sftp.ini")))

    assert test_config.sftp_hostname == '0.0.0.0'


def test_username_is_read():
    creat_mock_ini_file()
    test_config = SFTPCredentials(str(os.path.join(config_file, "test_sftp.ini")))
    os.remove(str(os.path.join(config_file, "test_sftp.ini")))

    assert test_config.sftp_username == 'testuser'


def test_password_is_read():
    creat_mock_ini_file()
    test_config = SFTPCredentials(str(os.path.join(config_file, "test_sftp.ini")))
    os.remove(str(os.path.join(config_file, "test_sftp.ini")))

    assert test_config.sftp_password == 'testpassword'
