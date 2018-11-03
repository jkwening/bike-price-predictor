from csv import DictWriter, DictReader
import pandas as pd
import os

from utils.utils import DATA_PATH


class Manifest(object):
  """Manifest is used to track state and path of raw data files."""
  def __init__(self, path=DATA_PATH, filename='manifest.csv'):
    self._MANIFEST_PATH = os.path.join(path, filename)
    self._HEADERS = [
      'source', 'tablename', 'bike_type', 'filename', 'timestamp',
      'loaded', 'date_loaded'
    ]

  def get_fieldnames(self):
    """Return column headers for manifest.csv."""
    return self._HEADERS

  def update(self, from_data=False, from_list=[], overwrite=False):
    """Create manifest CSV file.

    Can create populate manifest from raw data or list of values not both.

    Args:
      from_data (bool): populate manifest file from available data files else
        create empty manifest with just headers (default True)
      from_list (:obj: list of :obj: dict): populate from list of dicts
        (default [])
      overwrite (bool): overwrite existing manifest file if it exists
        (default False)

    Returns:
      True if successful, False otherwise.
    """
    # Raise error if attempt to load from both data and list
    if from_data and from_list:
      raise SyntaxError('Cannot load from both raw data and list of data.')
    
    # Create new file if doesn't exist or requested
    if overwrite or not os.path.exists(self._MANIFEST_PATH):
      with open(self._MANIFEST_PATH, mode='w') as f:
        writer = DictWriter(f, fieldnames=self._HEADERS)
        writer.writeheader()

    # Raise error if file cannot be found
    if not os.path.exists(self._MANIFEST_PATH):
      raise FileNotFoundError(self._MANIFEST_PATH)

    manifest = dict()
    with open(self._MANIFEST_PATH) as f:
      reader = DictReader(f)
      for row in reader:
        manifest[row['filename']] = row

    # Process add from_list option
    if from_list and self._validate_from_list(from_list):
      for data in from_list:
        manifest[data['filename']] = data
      
      self._to_csv(manifest)
      return True
    
    # Process add from_data option
    if from_data:
      pass

    return True    

  def _validate_from_list(self, data_list):
    """Validate that the passed data has appropriate fieldnames.

    Args:
      data_list (:obj: list of :obj: dict): fieldname, value representation of
        the data file

    Returns:
      True if all passed data have appropriate manifest fieldnames, else
        raises ValueError
    """
    for data in data_list:
      # check keys in data are fielnames
      for key in data.keys():
        if key not in self._HEADERS:
          raise ValueError(f'Not a valid manifest fieldname: {key}')

      # check all manifest fieldnames are in key in data
      for fieldname in self._HEADERS:
        if fieldname not in data.keys():
          raise ValueError(f'Data missing manifest fieldname: {fieldname}')

    return True

  def _to_csv(self, manifest):
    """Write manifest to csv."""
    with open(self._MANIFEST_PATH, 'w') as f:
      writer = DictWriter(f, fieldnames=self._HEADERS)
      writer.writeheader()

      for data in manifest.values():
        writer.writerow(data)
  