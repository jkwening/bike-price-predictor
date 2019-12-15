import os
from datetime import datetime

TIMESTAMP = datetime.now().strftime('%m%d%Y')
TESTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,
                                         'tests'))
DATA_PATH = os.path.abspath(os.path.join(TESTS_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(TESTS_DIR, 'test_data'))
MUNGED_DATA_PATH = os.path.abspath(os.path.join(TESTS_DIR, 'munged_data'))
