import unittest
from pprint import pprint

from ingestion.ingestion_mediator import IngestionMediator
from tests.unit_test_utils import DATA_PATH


class ManifestTestCase(unittest.TestCase):
    def setUp(self):
        self._mediator = IngestionMediator(data_path=DATA_PATH)

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

    def test_clean_source(self):
        df = self._mediator.clean_source(source='jenson')

        # Case 1: prod fields in merged dateframe
        cols = df.columns.tolist()
        for field in self._mediator._cleaner._FIELD_NAMES[:8]:
            self.assertTrue(field in cols,
                            msg=f'{field} not in merged columns: {cols}')

        print(df.head())
        print('\n', df.columns)
        print(df.shape)
        print(df.description.count())

    def test_get_table_pairs(self):
        result = self._mediator.aggregate_data()
        pprint(result)


if __name__ == '__main__':
    unittest.main()
