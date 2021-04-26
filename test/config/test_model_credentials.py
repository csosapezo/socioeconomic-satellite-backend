import os

import configparser

import config
from config.model_paths import ModelPath

config_file = os.path.abspath(os.path.join(os.path.dirname(config.model_paths.__file__), "init_files"))


def creat_mock_ini_file():
    mock = configparser.ConfigParser()
    mock["MODELS"] = {
        'ROOF_SEGMENTATION_PATH': 'foo_path.h5',
        'INCOME_DETERMINATION_PATH': 'bar_path.h5'
    }

    with open(str(os.path.join(config_file, "test_models.ini")), 'w') as configfile:
        mock.write(configfile)


def test_roof_segmentation_path_is_read():
    creat_mock_ini_file()
    test_config = ModelPath(str(os.path.join(config_file, "test_models.ini")))
    os.remove(str(os.path.join(config_file, "test_models.ini")))

    assert test_config.roof_segmentation_model_path == 'foo_path.h5'


def test_income_determination_is_read():
    creat_mock_ini_file()
    test_config = ModelPath(str(os.path.join(config_file, "test_models.ini")))
    os.remove(str(os.path.join(config_file, "test_models.ini")))

    assert test_config.income_level_determination_model_path == 'bar_path.h5'
