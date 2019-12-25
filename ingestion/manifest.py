import os
from csv import DictWriter, DictReader

from utils.utils import DATA_PATH, MUNGED_DATA_PATH


class Manifest(object):
    """Manifest is used to track state and path of raw data files."""

    def __init__(self, mediator, path=DATA_PATH, filename='manifest.csv'):
        self._mediator = mediator
        self._DATA_PATH = path
        self._MANIFEST_PATH = os.path.join(path, filename)
        self._HEADERS = [
            'site', 'tablename', 'bike_type', 'filename', 'timestamp',
            'loaded', 'date_loaded'
        ]

    def get_fieldnames(self):
        """Return column headers for manifest.csv."""
        return self._HEADERS

    def update(self, from_data=False, from_list=[], overwrite=False) -> bool:
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

        return False

    def _validate_from_list(self, data_list):
        """Validate that the passed data has appropriate fieldnames.

    Args:
      data_list (:obj: list of :obj: dict): fieldname, value representation of
        the data file

    Returns:
      True if all passed data have appropriate manifest fieldnames, else
        raises ValueError
    """
        print(f'[Manifest._validate_from_list()]')
        for data in data_list:
            # check keys in data are fieldnames
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
        with open(self._MANIFEST_PATH, 'w', encoding='utf-8') as f:
            writer = DictWriter(f, fieldnames=self._HEADERS)
            writer.writeheader()

            for data in manifest.values():
                writer.writerow(data)

    def get_all_rows(self) -> list:
        """Return list of dict objects representing all rows in manifest.csv."""
        rows = list()
        with open(self._MANIFEST_PATH, encoding='utf-8') as f:
            reader = DictReader(f)

            for row in reader:
                rows.append(row)

        return rows

    def get_unique_spec_fieldnames(self):
        """Return set of fieldnames used in all spec files in manifest.csv."""
        exclude_fieldnames = ['site', 'product_id']  # exclude primary key fieldnames
        rows = self.get_all_rows()
        spec_fieldnames = set()

        for row in rows:
            if row['tablename'] == 'product_specs':
                filepath = os.path.join(self._DATA_PATH, row['timestamp'], row['filename'])
                with open(filepath, encoding='utf-8') as f:
                    fieldnames = DictReader(f).fieldnames

                    for fieldname in fieldnames:
                        if fieldname in exclude_fieldnames:
                            continue
                        spec_fieldnames.add(fieldname)

        return spec_fieldnames

    def get_product_rows(self):
        """Get rows for products raw files in manifest.csv."""
        prod_rows = list()
        rows = self.get_all_rows()

        for row in rows:
            if row['tablename'] == 'products':
                prod_rows.append(row)

        return prod_rows

    def get_specs_rows(self):
        """Get rows for product specs raw files in manifest.csv."""
        specs_rows = list()
        rows = self.get_all_rows()

        for row in rows:
            if row['tablename'] == 'product_specs':
                specs_rows.append(row)

        return specs_rows

    def get_rows_matching(self, sources: list = [], tablenames: list = [],
                          bike_types: list = [], loaded: list = []) -> list:
        """Return list of manifest rows matching provided arguments."""
        matching_rows = list()
        with open(self._MANIFEST_PATH, encoding='utf-8') as f:
            reader = DictReader(f)

            for row in reader:
                if sources and row['site'] not in sources:
                    continue

                if tablenames and row['tablename'] not in tablenames:
                    continue

                if bike_types and row['bike_type'] not in bike_types:
                    continue

                if loaded and row['loaded'] not in loaded:
                    continue

                matching_rows.append(row)

        return matching_rows

    def get_filepath_for_row(self, row: dict) -> str:
        """Returns the absolute filepath for the data in manifest row."""
        return os.path.join(self._DATA_PATH, row['timestamp'], row['filename'])

    def get_table_pairs(self) -> dict:
        """For each site, bike_type get filepath for prods and specs data.

        Return dict: {site: {bike_type: {tablename: filepath}} where
            tablename is "products" or "product_specs"
        """
        pairs = dict()

        for row in self.get_all_rows():
            # Get or set default for site
            site_dict = pairs.setdefault(row['site'], {})
            # Get or set default for bike_type
            bike_type_dict = site_dict.setdefault(row['bike_type'], {})
            # Set value for tablename
            file_path = self.get_filepath_for_row(row)
            bike_type_dict[row['tablename']] = file_path
        return pairs


class MungedManifest(Manifest):
    def __init__(self, mediator, path=MUNGED_DATA_PATH,
                 filename='munged_manifest.csv'):
        super(MungedManifest, self).__init__(mediator, path, filename)
        # Reset modify default headers
        self._HEADERS = [
            'site', 'tablename', 'filename', 'timestamp',
            'loaded', 'date_loaded'
        ]
