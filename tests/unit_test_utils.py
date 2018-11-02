import os
from datetime import datetime

TIMESTAMP = datetime.now().strftime('%m%d%Y')
TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(TESTS_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(TESTS_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(TESTS_DIR, 'test_html'))
