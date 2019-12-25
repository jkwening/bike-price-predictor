import unittest

from ingestion.ingestion_mediator import IngestionMediator
from utils.unit_test_utils import DATA_PATH, MUNGED_DATA_PATH


class IngestionMediatorTestCase(unittest.TestCase):
    def setUp(self):
        self._mediator = IngestionMediator(data_path=DATA_PATH,
                                           munged_data_path=MUNGED_DATA_PATH)

    # TODO: add more testing data, needs another specs and two prods
    def test_load_manifest_row_to_db(self):
        """Test IngestionMediator._load_manifest_row_to_db(row)."""
        # manually initialize database connection
        self._mediator._ingest.connect()

        # testing data
        comp_road_spec_row = self._mediator._manifest.get_rows_matching(
            sources=['competitive'], tablenames=['product_specs'],
            bike_types=['road'])[0]
        print(comp_road_spec_row)

        result = self._mediator._load_manifest_row_to_db(row=comp_road_spec_row)
        self.assertTrue(result, msg='Should have loaded row to database.')

        # manually close database connection
        self._mediator._ingest.close()

    def test_load_to_database(self):
        """Test IngestionMediator._load_to_database(drop_tables=True)."""
        sources = ['nashbar']
        self._mediator._load_to_database(sources=sources, drop_tables=True)

    def test_complete_update(self):
        """Test IngestionMediator.update(from_manifest=False, drop_tables=True).
    
    Note - use 'sources=['competitive']" for quick running test case
    """
        sources = ['competitive']
        self._mediator.update(sources=sources, from_manifest=False,
                              drop_tables=True)

    def test_update_default(self):
        """Test IngestionMediator.update(drop_tables=True)."""
        sources = ['competitive']
        self._mediator.update(sources=sources, from_manifest=True,
                              drop_tables=True)

    def test_transform_raw_data(self):
        result = self._mediator.transform_raw_data(source='jenson')

        # Case 1: check returns appropriate field headings
        for field in result:
            self.assertTrue(field in self._mediator._munged_manifest._HEADERS,
                            msg=f'{field} not in self._mediator._munged_manifest._HEADERS')

        # Case 2: check correct values
        self.assertEqual('jenson', result['site'])
        self.assertEqual('munged', result['tablename'],)
        self.assertEqual('jenson_munged.csv', result['filename'],)
        self.assertEqual(self._mediator._cleaner._TIMESTAMP, result['timestamp'],)
        self.assertEqual(False, result['loaded'],)
        self.assertEqual(None, result['date_loaded'],)

    def test_transform_from_manifest(self):
        # Case 1: only update munged manifest and save cleaned data
        self._mediator.transform_from_manifest()
        # Case 2: only create combine df and save to csv
        self._mediator.transform_from_manifest(update_munged_manifest=False,
                                               save_cleaned_data=False, combine=True,
                                               save_combined=True)

    def test_aggregate_data(self):
        self._mediator.aggregate_data()


if __name__ == '__main__':
    unittest.main()
