import os
from datetime import datetime
from csv import DictReader
from configparser import ConfigParser

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DATA_PATH = os.path.abspath(os.path.join(ROOT_PATH, 'data'))
MUNGED_DATA_PATH = os.path.abspath(os.path.join(ROOT_PATH, 'munged_data'))
TIMESTAMP = datetime.now().strftime('%m%d%Y')
CONFIG_FILE = os.path.abspath(os.path.join(ROOT_PATH, 'config.ini'))


def create_directory_if_missing(file_path: str):
    """
    Ensure there is a directory for given filepath, if doesn't exists it creates ones.

    :param file_path: file path for where to write and save csv file
    :type file_path: string

    :return: None
    """
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)


def get_fieldnames_from_file(filepath: str) -> list:
    """Returns column headers for csv files."""
    with(open(filepath, encoding='utf-8')) as f:
        fieldnames = DictReader(f).fieldnames
    return fieldnames


def config(section: str, filename=CONFIG_FILE,):
    """Returns parameters for given section of the config.ini file."""
    parser = ConfigParser()
    parser.read(filename)

    # get section parameters
    pars = dict()
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            pars[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return pars
