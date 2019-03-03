import os
import re
from datetime import datetime

MODULE_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_PATH, os.pardir, 'data'))
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


def get_bike_type_from_desc(desc):
    BIKE_TYPES_LIST = [  # order matters for fork, frame, kid, girl, and bmx as qualifiers
        'frame', 'fork', 'kid', 'girl', 'e-bike', 'bmx', 'city', 'commuter', 'comfort',
        'cruiser', 'fat', 'triathlon', 'adventure', 'touring', 'urban',
        'track', 'road', 'mountain', 'cyclocross', 'hybrid',
        'gravel'
    ]

    for bike_type in BIKE_TYPES_LIST:
        if re.search(re.escape(bike_type), desc, re.IGNORECASE):
            return bike_type

    return None
