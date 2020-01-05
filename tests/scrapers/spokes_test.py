# python modules
import os
import unittest

from bs4 import BeautifulSoup

# package modules
from scrapers.spokes import Spokes
from utils.unit_test_utils import DATA_PATH, TIMESTAMP


class CityBikesTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Spokes(save_data_path=DATA_PATH)
        self._bike_type = 'commuter_urban'

    def test_get_categories(self):
        categories = [
            'road_bikes',
            'mountain_bikes',
            'cyclocross',
            'commuter_urban',
            'comfort',
            'cruiser',
            'fitness',
            'electric',
            'hybrid_bike',
            'childrens',
            'other',
            'bmx'
        ]

        result = self._scraper._get_categories()
        print('\nCategories:', result)
        for key in result.keys():
            self.assertTrue(key in categories,
                            msg=f'{key} not in {categories}')

    def test_get_prods_listing(self):
        self._scraper._page_size = 30  # constrain maximum num of prods on page
        categories = self._scraper._get_categories()
        endpoint = categories[self._bike_type]['href']
        soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
            endpoint), 'lxml')

        # Verify product listings fetch
        self._scraper._get_prods_on_current_listings_page(soup, self._bike_type)
        num_prods = len(self._scraper._products)
        expected_num_prods = int(categories[self._bike_type]['count'])
        if expected_num_prods > self._scraper._page_size:
            self.assertEqual(num_prods, self._scraper._page_size,
                             msg=f'{num_prods} product, expected: {self._scraper._page_size}.')
        else:
            self.assertEqual(expected_num_prods, num_prods,
                             msg=f'{num_prods} product, expected: {expected_num_prods}.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'spokes_prods_all.csv')
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
                    'fork', 'cassette_rear_cogs', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
