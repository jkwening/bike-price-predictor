import os
from datetime import datetime

MODULE_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_PATH, os.pardir, 'data'))
TIMESTAMP = datetime.now().strftime('%Y%m%d')

def create_directory_if_missing(file_path):
    """
    Ensure there is a directory for given filepath, if doesn't exists it creates ones.

    :param file_path: file path for where to write and save csv file
    :type file_path: string

    :return: None
    """
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
