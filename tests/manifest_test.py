import unittest
import os
from csv import DictReader, DictWriter

from ingestion.manifest import Manifest
from tests.unit_test_utils import DATA_PATH


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

  def test_update_empty(self):
    """Test case for manifest.update()"""
    # Delete manifest.csv files if it exists
    if os.path.exists(self._MANIFEST_PATH):
      os.remove(self._MANIFEST_PATH)
    
    # case 1 - create empty manifest.csv
    self.assertFalse(os.path.exists(self._MANIFEST_PATH),
      msg='Failed to delete manifest.csv before testing update()!')
    self._manifest.update()
    self.assertTrue(os.path.exists(self._MANIFEST_PATH),
      msg='Failed to create empty manifest file!')
    with open(self._MANIFEST_PATH) as f:
      rows = f.readlines()
      self.assertEqual(1, len(rows),
        msg='manifest.csv should contain only the headers!')

    # case 2 - overwrite existing manifest.csv
    # Populate manifest.csv with dummy data
    with open(self._MANIFEST_PATH, mode='w') as f:
      writer = DictWriter(f, fieldnames=self._manifest.get_fieldnames())
      writer.writeheader()
      for data in self._DUMMY_DATA:
        writer.writerow(data)

    # Verify manifest.csv now has 3 lintes: headers + 2 rows dummy data
    with open(self._MANIFEST_PATH) as f:
      rows = f.readlines()
      self.assertEqual(3, len(rows),
        msg='manifest.csv should contain three rows!')

    # Overwrite manifest.csv and verify only contains headers
    self._manifest.update(overwrite=True)
    with open(self._MANIFEST_PATH) as f:
      rows = f.readlines()
      self.assertEqual(1, len(rows),
        msg='manifest.csv should contain only the headers!')

  def test_update_from_both(self):
    """Test case for manifest.update(from_data=True, from_list=[...])"""
    self.assertRaises(SyntaxError, self._manifest.update, from_data=True,
      from_list=[self._DUMMY_DATA])

# TODO - need to complete: need to generate test csv files with
#     timestamp organized folder structure like prod
  def test_update_from_data(self):
    """Test case for manifest.update(from_data=True)"""
    # Delete any existing test_manifest.csv files and then create empty
    self.assertEqual(False, True)

  def test_update_from_list(self):
    """Test case for manifest.update(from_list=[...])"""
    # Populate test_manifest.csv with some rows
    self.assertTrue(self._manifest.update(from_list=self._DUMMY_DATA,
      overwrite=True),
      msg='Failed to create/overwrite existing test_manifest.csv')

    data1 = {
      'source': 'nashbar', 'prod/specs': 'prod', 'bike_type': 'road_bike',
      'filename': 'nashbar_prod_listing_test_data.csv',
      'timestamp': '12252018', 'loaded': 'yes', 'date_loaded': ''
    }
    data2 = {
      'source': 'competitive', 'prod/specs': 'specs', 'bike_type': 'cyclocross',
      'filename': 'competitive_prod_specs_test_data.csv',
      'timestamp': '10302018', 'loaded': '', 'date_loaded': ''
    }

    # Add sample data to manifest
    self.assertTrue(self._manifest.update(from_list=[data1, data2]),
      msg='Update from list returned false')

    in_manifest_data1 = False
    in_manifest_data2 = False
    with open(self._MANIFEST_PATH) as f:
      reader = DictReader(f, fieldnames=self._manifest.get_fieldnames())
      
      for row in reader:
        if in_manifest_data1 and in_manifest_data2:
          break

        if row['filename'] == data1['filename']:
          self.assertEqual(row['timestamp'], data1['timestamp'],
            msg='Should have updated timestamp')
          self.assertEqual(row['loaded'], data1['loaded'],
            msg='Should have updated loaded value')
          in_manifest_data1 = True
          continue

        if row['filename'] == data2['filename']:
          self.assertEqual(row['source'], data2['source'],
            msg='Should have source = competitive')
          self.assertEqual(row['bike_type'], data2['bike_type'],
            msg='Should have bike_type = cyclocross')
          in_manifest_data2 = True
          continue

    self.assertTrue(in_manifest_data1 and in_manifest_data2,
      msg='manifest did not have updated data')

  def test_validate_from_list(self):
    """Test case for manifest._vilidate_from_list()."""
    # case 1: Raise ValueError for missing or extra fieldnames
    data1 = {
      'source': 'nashbar', 'prod/specs': 'prod', 'bike_type': 'road_bike',
      'filename': 'nashbar_prod_listing_test_data.csv',
      'timestamp': '12252018', 'hello_world': 'yes', 'date_loaded': ''
    }
    data2 = {
      'source': 'competitive', 'prod/specs': 'specs', 'bike_type': 'cyclocross',
      'filename': 'competitive_prod_specs_test_data.csv',
      'loaded': '', 'date_loaded': ''
    }
    self.assertRaises(ValueError, self._manifest._validate_from_list, [data1])
    self.assertRaises(ValueError, self._manifest._validate_from_list, [data2])

    # case 2: Correct fieldnames
    self.assertTrue(self._manifest._validate_from_list(self._DUMMY_DATA),
      msg="Should pass fieldname validation")


if __name__ == '__main__':
    unittest.main()
