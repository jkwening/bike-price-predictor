import unittest
import pandas as pd

from ingestion.cleaner import Cleaner
from ingestion.ingestion_mediator import IngestionMediator
from tests.unit_test_utils import DATA_PATH, MUNGED_DATA_PATH


class CleanerTestCase(unittest.TestCase):
    def setUp(self):
        self._mediator = IngestionMediator(data_path=DATA_PATH)
        self._cleaner = Cleaner(mediator=self._mediator, save_data_path=MUNGED_DATA_PATH)

    def test_merge_source(self):
        specs_row = self._mediator.get_rows_matching(sources=['jenson'],
                                                     bike_types=['all'],
                                                     tablenames=['product_specs'])[0]
        specs_df = pd.read_csv(self._mediator.get_filepath_for_manifest_row(specs_row))
        num_rows, num_cols = specs_df.shape

        df = self._cleaner.merge_source(source='jenson')
        print('[test_merge_source]: columns\n', df.columns)

        # Case 1; Same number of rows but more columns
        self.assertEqual(num_rows, df.shape[0],
                         msg=f'Expected {num_rows}; Result: {df.shape}')
        self.assertGreater(df.shape[1], num_cols,
                           msg=f'Expected greater than {num_cols} colums; Result: {df.shape}')

        # Case 2: prod fields in merged dateframe
        cols = df.columns.tolist()
        for field in self._cleaner._FIELD_NAMES[:8]:
            self.assertTrue(field in cols,
                            msg=f'{field} not in merged columns: {cols}')

    def test_jenson_cleaner(self):
        merged_df = self._cleaner.merge_source(source='jenson')
        munged_df = self._cleaner._jenson_cleaner(merged_df)

        cols = munged_df.columns.tolist()
        for field in self._cleaner._FIELD_NAMES:
            self.assertTrue(field in cols,
                            msg=f'{field} not in merged columns: {cols}')

    def test_nashbar_cleaner(self):
        merged_df = self._cleaner.merge_source(source='nashbar')
        munged_df = self._cleaner._nashbar_cleaner(merged_df)

        cols = munged_df.columns.tolist()
        for field in self._cleaner._FIELD_NAMES:
            self.assertTrue(field in cols,
                            msg=f'{field} not in merged columns: {cols}')

    def test_trek_cleaner(self):
        merged_df = self._cleaner.merge_source(source='trek')
        munged_df = self._cleaner._trek_cleaner(merged_df)

        cols = munged_df.columns.tolist()
        for field in self._cleaner._FIELD_NAMES:
            self.assertTrue(field in cols,
                            msg=f'{field} not in merged columns: {cols}')

    def test_rei_cleaner(self):
        merged_df = self._cleaner.merge_source(source='rei')
        munged_df = self._cleaner._rei_cleaner(merged_df)

        cols = munged_df.columns.tolist()
        for field in self._cleaner._FIELD_NAMES:
            self.assertTrue(field in cols,
                            msg=f'{field} not in merged columns: {cols}')

    def test_citybikes_cleaner(self):
        merged_df = self._cleaner.merge_source(source='citybikes')
        munged_df = self._cleaner._citybikes_cleaner(merged_df)

        cols = munged_df.columns.tolist()
        for field in self._cleaner._FIELD_NAMES:
            self.assertTrue(field in cols,
                            msg=f'{field} not in merged columns: {cols}')

    def test_proshop_cleaner(self):
        merged_df = self._cleaner.merge_source(source='proshop')
        munged_df = self._cleaner._proshop_cleaner(merged_df)

        cols = munged_df.columns.tolist()
        for field in self._cleaner._FIELD_NAMES:
            self.assertTrue(field in cols,
                            msg=f'{field} not in merged columns: {cols}')

    def test_contebikes_cleaner(self):
        merged_df = self._cleaner.merge_source(source='contebikes')
        munged_df = self._cleaner._contebikes_cleaner(merged_df)

        cols = munged_df.columns.tolist()
        for field in self._cleaner._FIELD_NAMES:
            self.assertTrue(field in cols,
                            msg=f'{field} not in merged columns: {cols}')

    def test_giant_cleaner(self):
        merged_df = self._cleaner.merge_source(source='giant')
        munged_df = self._cleaner._giant_cleaner(merged_df)

        cols = munged_df.columns.tolist()
        for field in self._cleaner._FIELD_NAMES:
            self.assertTrue(field in cols,
                            msg=f'{field} not in merged columns: {cols}')

    def test_litespeed_cleaner(self):
        merged_df = self._cleaner.merge_source(source='litespeed')
        munged_df = self._cleaner._litespeed_cleaner(merged_df)

        cols = munged_df.columns.tolist()
        for field in self._cleaner._FIELD_NAMES:
            self.assertTrue(field in cols,
                            msg=f'{field} not in merged columns: {cols}')

    def test_lynskey_cleaner(self):
        merged_df = self._cleaner.merge_source(source='lynskey')
        munged_df = self._cleaner._lynskey_cleaner(merged_df)

        cols = munged_df.columns.tolist()
        for field in self._cleaner._FIELD_NAMES:
            self.assertTrue(field in cols,
                            msg=f'{field} not in merged columns: {cols}')

    def test_spokes_cleaner(self):
        merged_df = self._cleaner.merge_source(source='spokes')
        munged_df = self._cleaner._spokes_cleaner(merged_df)

        cols = munged_df.columns.tolist()
        for field in self._cleaner._FIELD_NAMES:
            self.assertTrue(field in cols,
                            msg=f'{field} not in merged columns: {cols}')

    def test_competitive_cleaner(self):
        merged_df = self._cleaner.merge_source(source='competitive')
        munged_df = self._cleaner._competitive_cleaner(merged_df)

        cols = munged_df.columns.tolist()
        for field in self._cleaner._FIELD_NAMES:
            self.assertTrue(field in cols,
                            msg=f'{field} not in merged columns: {cols}')


if __name__ == '__main__':
    unittest.main()

