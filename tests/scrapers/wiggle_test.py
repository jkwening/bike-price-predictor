# python modules
import os
import unittest

from bs4 import BeautifulSoup

# package modules
from scrapers.wiggle import Wiggle
from utils.unit_test_utils import DATA_PATH, TIMESTAMP


class WiggleTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Wiggle(save_data_path=DATA_PATH)
        self._bike_type = 'urban_bikes'
        self._categories = ['road_bikes', 'mountain_bikes',
                            'cyclocross_bikes', 'adventure_bikes',
                            'touring_bikes', 'urban_bikes',
                            'track_bikes', 'time_trial_bikes']

    def test_get_categories(self):
        result = self._scraper._get_categories()
        print('\nCategories', result)
        self.assertEqual(len(self._categories), len(result))
        for key in result.keys():
            self.assertTrue(key in self._categories,
                            msg=f'{key} not in {self._categories}.')

    def test_subtypes(self):
        bike_type = 'mountain_bikes'
        expected = ['hard_tail_mountain_bikes',
                    'full_suspension_mountain_bikes']
        result = self._scraper._get_subtypes()
        print('Subtypes:', result)
        self.assertEqual(len(self._categories), len(result))
        for key in result.keys():
            self.assertTrue(key in self._categories,
                            msg=f'{key} not in {self._categories}.')
        subtypes = result[bike_type].keys()
        self.assertEqual(len(expected), len(subtypes))
        for subtype in subtypes:
            self.assertTrue(subtype in expected,
                            msg=f'{subtype} not in {expected}')

    def test_get_prods_listings(self):
        bike_cats = self._scraper._get_subtypes()
        expected_num_prods = 0
        for subtype, values in bike_cats[self._bike_type].items():
            endpoint = values['href']
            soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
                url=endpoint, page_size=24), 'lxml')

            # Verify product listings fetch
            self._scraper._get_prods_on_current_listings_page(
                soup, self._bike_type, subtype
            )
            prod_count = values['count']
            if prod_count > 24:
                expected_num_prods += 24
            else:
                expected_num_prods += prod_count

        num_prods = len(self._scraper._products)
        self.assertEqual(expected_num_prods, num_prods,
                         msg=f'{num_prods} product, expected: {expected_num_prods}.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'wiggle_prods_all.csv')
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
                    'fork', 'cassette', 'saddle', 'seat_post']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
