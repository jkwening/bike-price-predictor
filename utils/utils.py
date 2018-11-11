import os
from datetime import datetime
from csv import DictReader

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DATA_PATH = os.path.abspath(os.path.join(ROOT_PATH, 'data'))
TIMESTAMP = datetime.now().strftime('%m%d%Y')

def create_directory_if_missing(file_path):
    """
    Ensure there is a directory for given filepath, if doesn't exists it creates ones.

    :param file_path: file path for where to write and save csv file
    :type file_path: string

    :return: None
    """
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)

def get_fieldnames_from_file(filepath):
  """Returns column headers for csv files."""
  with(open(filepath, encoding='utf-8')) as f:
    fieldnames = DictReader(f).fieldnames
  return fieldnames
    