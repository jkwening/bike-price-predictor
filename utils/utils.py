import os
import re
from datetime import datetime
from csv import DictReader
from configparser import ConfigParser

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DATA_PATH = os.path.join(ROOT_PATH, 'data')
RAW_DATA_PATH = os.path.join(DATA_PATH, 'raw_data')
MUNGED_DATA_PATH = os.path.join(DATA_PATH, 'munged_data')
COMBINED_MUNGED_PATH = os.path.join(MUNGED_DATA_PATH, 'combined')
MERGED_RAW_PATH = os.path.join(DATA_PATH, 'merged_raw_data')
TIMESTAMP = datetime.now().strftime('%Y-%m-%d')
DATE_YEAR, DATE_MON, DATE_DAY = TIMESTAMP.split('-')
CONFIG_FILE = os.path.join(ROOT_PATH, 'config.ini')
SOURCES = [
    'bike_doctor', 'citybikes', 'contebikes', 'jenson',
    'litespeed', 'lynskey', 'proshop', 'spokes', 'trek'
]
# SOURCES = [
#     'backcountry', 'bicycle_warehouse', 'bike_doctor', 'canyon', 'citybikes',
#     'competitive', 'contebikes', 'eriks', 'giant',
#     'jenson', 'litespeed', 'lynskey', 'nashbar', 'proshop',
#     'rei', 'specialized', 'spokes', 'trek', 'wiggle'
# ]
SOURCES_EXCLUDE = [
    'foxvalley'
]
GROUPSET_RANKING = {
    'shimano claris': 1,
    'shimano sora': 2,
    'shimano tiagra': 2.5,
    'shimano 105': 3,
    'shimano ultegra': 4,
    'shimano ultegra di2': 5.5,
    'shimano dura-ace': 5,
    'shimano dura-ace di2': 6.25,
    'sram apex': 2,
    'sram rival': 3,
    'sram s700': 3,
    'sram force': 4,
    'sram force etap': 4.5,
    'sram red': 5,
    'sram red etap': 6,
    'sram red etap axs': 6.5,
    'campagnolo veloce': 2,
    'campagnolo centaur': 2.5,
    'campagnolo athena': 3,
    'campagnolo potenza': 4,
    'campagnolo chorus': 4,
    'campagnolo athena eps': 3.5,
    'campagnolo record': 5,
    'campagnolo chorus eps': 4.5,
    'campagnolo super record': 5.25,
    'campagnolo record eps': 5.5,
    'campagnolo super record eps': 7,
    'shimano tourney': 0.5,
    'shimano altus': 1,
    'shimano acera': 1.5,
    'shimano alivio': 2,
    'shimano deore': 2.75,
    'shimano slx': 3,
    'shimano zee': 3,
    'shimano deore xt': 4,
    'shimano xt': 4,  # ?
    'shimano saint': 4.5,
    'shimano xt di2': 4,
    'shimano xtr': 5,
    'shimano xtr di2': 6,
    'sram x3': 0.5,
    'sram x4': 1.5,
    'sram x5': 2,
    'sram x7': 2.25,
    'sram x9': 2.6,
    'sram sx eagle': 2.75,
    'sram nx': 3,
    'sram gx dh': 3,
    'sram gx': 3.25,
    'sram gx eagle': 3.5,
    'sram x1': 3.75,
    'sram xO1 dh': 4.25,
    'sram xO': 4.0,
    'sram xO1': 4.25,
    'sram xx': 4.5,
    'sram xx1': 5,
    'sram xO1 eagle': 4.75,
    'sram xx1 eagle': 6,
    'sram eagle axs': 6.5,
    'sram via': 3.5,
    'shimano 7-speed': 0.5,
    'shimano 8-speed': 1,
    'shimano 9-speed': 2,
    'shimano 10-speed': 2.5,
    'sram 8-speed': 0.5,
    'sram 9-speed': 1,
    'sram 10-speed': 2,
}


def create_directory_if_missing(file_path: str):
    """
    Ensure there is a directory for given filepath, if doesn't exists it creates ones.

    :param file_path: file path for where to write and save csv file
    :type file_path: string

    :return: None
    """
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)


def get_bike_type_from_desc(desc):
    bike_types_list = [  # order matters for fork, frame, kid, girl, and bmx as qualifiers
        'frame', 'frameset', 'fork', 'kid', 'girl', 'e-bike', 'bmx', 'city', 'commuter', 'comfort',
        'cruiser', 'fat', 'triathlon', 'adventure', 'touring', 'urban',
        'track', 'road', 'mountain', 'cyclocross', 'hybrid',
        'gravel'
    ]

    for bike_type in bike_types_list:
        if re.search(re.escape(bike_type), desc, re.IGNORECASE):
            return bike_type

    return None


def get_fieldnames_from_file(filepath: str) -> list:
    """Returns column headers for csv files."""
    with(open(filepath, encoding='utf-8')) as f:
        fieldnames = DictReader(f).fieldnames
    return fieldnames


def config(section: str, filename=CONFIG_FILE, ):
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
