import os

import configparser

import config
from config.app_config import AppConfig

config_file = os.path.abspath(os.path.join(os.path.dirname(config.app_config.__file__), "init_files"))


def creat_mock_ini_file(debug):
    mock = configparser.ConfigParser()
    mock["DEVELOPMENT"] = {
        'DEBUG': debug,
        'PORT': '5000',
        'HOST': '0.0.0.0',
        'SECRET_KEY': '70e34e3bce494540edafd078c6109645',
        'CORS_HEADERS': 'Access-Control-Allow-Origin'
    }

    with open(str(os.path.join(config_file, "test_app.ini")), 'w') as configfile:
        mock.write(configfile)


def test_debug_true_is_read():
    creat_mock_ini_file("True")
    test_config = AppConfig('DEVELOPMENT', str(os.path.join(config_file, "test_app.ini")))
    os.remove(str(os.path.join(config_file, "test_app.ini")))

    assert test_config.DEBUG is True


def test_debug_false_is_read():
    creat_mock_ini_file("False")
    test_config = AppConfig('DEVELOPMENT', str(os.path.join(config_file, "test_app.ini")))
    os.remove(str(os.path.join(config_file, "test_app.ini")))

    assert test_config.DEBUG is False


def test_port_is_read():
    creat_mock_ini_file("True")
    test_config = AppConfig('DEVELOPMENT', str(os.path.join(config_file, "test_app.ini")))
    os.remove(str(os.path.join(config_file, "test_app.ini")))

    assert test_config.PORT == 5000


def test_host_is_read():
    creat_mock_ini_file("True")
    test_config = AppConfig('DEVELOPMENT', str(os.path.join(config_file, "test_app.ini")))
    os.remove(str(os.path.join(config_file, "test_app.ini")))

    assert test_config.HOST == '0.0.0.0'


def test_secret_key_is_read():
    creat_mock_ini_file("True")
    test_config = AppConfig('DEVELOPMENT', str(os.path.join(config_file, "test_app.ini")))
    os.remove(str(os.path.join(config_file, "test_app.ini")))

    assert test_config.SECRET_KEY == '70e34e3bce494540edafd078c6109645'


def test_cors_headers_is_read():
    creat_mock_ini_file("True")
    test_config = AppConfig('DEVELOPMENT')
    os.remove(str(os.path.join(config_file, "test_app.ini")))

    assert test_config.CORS_HEADERS == 'Access-Control-Allow-Origin'
