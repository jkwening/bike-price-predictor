# python modules
import os
import unittest

from bs4 import BeautifulSoup

# package modules
from scrapers.nashbar import NashBar
from utils.unit_test_utils import DATA_PATH, TIMESTAMP


class NashBarTestCase(unittest.TestCase):
    def setUp(self):
        # use smaller page_size for testing purposes
        self._scraper = NashBar(save_data_path=DATA_PATH)
        self._bike_type = 'gravel_bikes'
        self._categories = ['cyclocross_bikes', 'gravel_bikes',
                      'bike_hybrids_commuters_cruisers',
                      'mountain_bikes', 'road_bicycles',
                      'single_speed_fixed_gear_bikes']

    def test_get_categories(self):
        result = self._scraper._get_categories()
        print('\nCategories:', result)
        self.assertEqual(len(self._categories), len(result),
                         msg=f'Expected {len(self._categories)}; result {len(result)}')
        for key in result:
            self.assertTrue(key in self._categories,
                            msg=f'{key} is not in {self._categories}!')

    def test_get_subtypes(self):
        bike_type = 'road_bicycles'
        expected_subtypes = [
            'drop_bar_road_bikes_frames',
            'electric_road_bikes',
            'flatbar_road_bikes_frames',
            'touring_rando_endurance_bikes_road_frames'
        ]
        result = self._scraper._get_subtypes()
        print('Subtypes:', result)
        self.assertEqual(len(self._categories), len(result),
                         msg='Number of bike types don\'t match.')
        for subtype in result[bike_type].keys():
            self.assertTrue(subtype in expected_subtypes,
                            msg=f'{subtype} not in {expected_subtypes}')

    def test_get_prods_listings(self):
        bike_cats = self._scraper._get_subtypes()
        for subtype, href in bike_cats[self._bike_type].items():
            soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
                endpoint=href), 'lxml')

            self._scraper._get_prods_on_current_listings_page(
                soup, self._bike_type, subtype
            )
        # Verify product listings fetch
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 1,
                        msg=f'There are {num_prods} product first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'nashbar_prods_all.csv')
        # Verify parsing product specs
        specs = self._scraper.get_product_specs(get_prods_from=prods_csv_path,
                                                bike_type=self._bike_type,
                                                to_csv=False)
        num_prods = len(self._scraper._products)
        num_specs = len(specs)
        self.assertEqual(num_prods, num_specs,
                         msg=f'Products size: {num_prods}, Specs size: {num_specs}')
        self._scraper._write_prod_specs_to_csv(specs=specs,
                                               bike_type=self._bike_type)

        # Verify spec fieldnames has minimum general fields:
        expected = ['site', 'product_id', 'frame',
                    'fork', 'cassette', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
