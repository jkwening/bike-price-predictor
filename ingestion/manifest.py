from csv import DictWriter

from utils.utils import *


class Manifest(object):
  """Manifest is used to track state and path of raw data files."""
  def __init__(self, path=DATA_PATH):
    self._MANIFEST_PATH = path
    self._HEADERS = [
      'source', 'prod/specs', 'bike_type', 'filename', 'timestamp',
      'loaded', 'date_loaded'
    ]

  def getFieldnames(self):
    """Return column headers for manifest.csv."""
    return self._HEADERS

  def create(self, from_data=False, from_list=[], overwrite=False):
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

    return True    

  def update(self, from_data=True, how_many_days=5, from_list=[]):
    """Update manifest CSV file.

    Can update manifest by default from available raw data or optionally from
    list of values - not both.
    Note: Will create manifest.csv if it doesn't already exist.

    Args:
      from_data (bool): use available data files (default True)
      from_list (:obj: list of :obj: dict): update from list of dicts
        (default [])

    Returns:
      True if successful, False otherwise
    """
    pass
