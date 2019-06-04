import unittest
import pandas as pd

from ingestion.cleaner import Cleaner
from ingestion.ingestion_mediator import IngestionMediator
from tests.unit_test_utils import DATA_PATH, MUNGED_DATA_PATH


class ManifestTestCase(unittest.TestCase):
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
        """
        [test_merge_source]: columns
 Index(['site', 'bike_type', 'product_id', 'href', 'description', 'brand',
       'price', 'msrp', 'Unnamed: 0', 'tape', 'brakes', 'battery',
       'headtube_diameter', 'handlebar_widths', 'rear_derailleur', 'bar_tape',
       'cable_routing', 'wheel_size', 'front_derailleur', 'shock', 'rotors',
       'dropout_style', 'bottom_bracket', 'rotor_size', 'headset_included',
       'stem_lengths', 'handlebar', 'seatclamp', 'frame', 'wheelset', 'fork',
       'cassette', 'front_tire', 'shifter', 'grips', 'pedals', 'drive_unit',
       'accessory_mounts', 'lights', 'shifters', 'approximate_weight',
       'crankset', 'weight', 'seatpost', 'saddle', 'brake_levers', 'headset',
       'rear_tire', 'handlebar_width', 'stem_length', 'intended_use',
       'seat_clamp', 'tires', 'bartape', 'motor', 'chain', 'rear_shock',
       'display', 'derailleurs', 'handlebars', 'seatpost_lengths',
       'crank_arm_lengths', 'stem'],
      dtype='object')
        :return:
        """
        merged_df = self._cleaner.merge_source(source='jenson')
        munged_df = self._cleaner._jenson_cleaner(merged_df)
        # print(munged_df[0:1])
        # print(munged_df.shape)
        print(munged_df.bike_type.unique().tolist())
        # print(munged_df.model_year.unique())
        # print(munged_df.loc[merged_df.bike_type == 'corona_store_exclusives', ['bike_type', 'intended_use']])


if __name__ == '__main__':
    unittest.main()
