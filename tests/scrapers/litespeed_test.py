# python modules
import os
import unittest
import json
from pprint import pprint

from bs4 import BeautifulSoup

# package modules
from scrapers.litespeed import LiteSpeed
from utils.unit_test_utils import DATA_PATH, TIMESTAMP


class SpecializedTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = LiteSpeed(save_data_path=DATA_PATH)
        self._bike_type = 'road'

    def test_get_subtypes(self):
        bike_type = 'mountain'
        expected = ['trail', 'trail_xc', 'xc']
        result = self._scraper._get_subtypes()
        print('Subtypes:', result)
        self.assertEqual(len(expected), len(result[bike_type]),
                         msg='Number of subtypes not equal.')
        for subtype in result[bike_type]:
            self.assertTrue(subtype in expected,
                            msg=f'{subtype} not in {expected}!')

    def test_fetch_prod_options(self):
        prod_id = 4297638248523
        result = self._scraper._fetch_prod_options(prod_id)
        print('Options:\n', result)
        expected_prod_name = 'T5'
        self.assertEqual(
            expected_prod_name,
            result['name'],
            msg='Product name is incorrect!'
        )

    def test_get_prods_listings(self):
        categories = self._scraper._get_subtypes()
        for subtype, href in categories[self._bike_type].items():
            soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
                endpoint=href), 'lxml')

            self._scraper._get_prods_on_current_listings_page(soup, self._bike_type,
                                                              subtype)
        # Verify product listings fetch
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 2,
                        msg=f'There are {num_prods} product first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'litespeed_prods_all.csv')
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
        expected = ['site', 'product_id', 'shifters',
                    'fork', 'cassette', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
