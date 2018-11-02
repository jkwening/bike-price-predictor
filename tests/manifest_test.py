import unittest
from csv import DictReader, DictWriter

from ingestion.manifest import Manifest
from tests.unit_test_utils import *


class ManifestTestCase(unittest.TestCase):
  def setUp(self):
    self._MANIFEST_PATH = os.path.join(DATA_PATH, 'test_manifest.csv')
    self._manifest = Manifest(path=self._MANIFEST_PATH)
    self._DUMMY_DATA = [
      {
        'source': 'nashbar', 'prod/specs': 'prod', 'bike_type': 'road_bike',
        'filename': 'nashbar_prod_listing_test_data.csv',
        'timestamp': '10302018', 'loaded': '', 'date_loaded': ''
      },
      {
        'source': 'performance', 'prod/specs': 'specs', 'bike_type': 'any',
        'filename': 'performance_prod_listing_test_data.csv',
        'timestamp': '10282018', 'loaded': '', 'date_loaded': ''
      }
    ]

  def test_create_empty(self):
    """Test case for Manifest.create()"""
    # Delete manifest.csv files if it exists
    if os.path.exists(self._MANIFEST_PATH):
      os.remove(self._MANIFEST_PATH)
    
    # case 1 - create empty manifest.csv
    self.assertFalse(os.path.exists(self._MANIFEST_PATH),
      msg='Failed to delete manifest.csv before testing create()!')
    self._manifest.create()
    self.assertTrue(os.path.exists(self._MANIFEST_PATH),
      msg='Failed to create empty manifest file!')
    with open(self._MANIFEST_PATH) as f:
      rows = f.readlines()
      self.assertEqual(1, len(rows),
        msg='manifest.csv should contain only the headers!')

    # case 2 - overwrite existing manifest.csv
    # Populate manifest.csv with dummy data
    with open(self._MANIFEST_PATH, mode='w') as f:
      writer = DictWriter(f, fieldnames=self._manifest.getFieldnames())
      writer.writeheader()
      for data in self._DUMMY_DATA:
        writer.writerow(data)

    # Verify manifest.csv now has 3 lintes: headers + 2 rows dummy data
    with open(self._MANIFEST_PATH) as f:
      rows = f.readlines()
      self.assertEqual(3, len(rows),
        msg='manifest.csv should contain three rows!')

    # Overwrite manifest.csv and verify only contains headers
    self._manifest.create(overwrite=True)
    with open(self._MANIFEST_PATH) as f:
      rows = f.readlines()
      self.assertEqual(1, len(rows),
        msg='manifest.csv should contain only the headers!')

  def test_create_from_both(self):
    """Test case for Manifest.create(from_data=True, from_list=[...])"""
    self.assertRaises(SyntaxError, self._manifest.create, from_data=True,
      from_list=[self._DUMMY_DATA])

  def test_create_from_data(self):
    """Test case for Manifest.create()"""
    # Delete any existing test_manifest.csv files and then create empty
    self.assertEqual(False, True)

  def test_create_from_list(self):
    """Test case for Manifest.create()"""
    # Delete any existing test_manifest.csv files and then create empty
    self.assertEqual(False, True)

  def test_update(self):
    """Test cases for Manifest.update()"""
    self.assertEqual(False, True)

if __name__ == '__main__':
    unittest.main()
