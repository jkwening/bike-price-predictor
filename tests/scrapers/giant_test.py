# python modules
import os
import unittest

from bs4 import BeautifulSoup

# package modules
from scrapers.giant import Giant
from utils.unit_test_utils import DATA_PATH, TIMESTAMP


class GiantTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Giant(save_data_path=DATA_PATH)
        self._bike_type = 'road_bikes'

    def test_get_categories(self):
        categories = [
            'road_bikes',
            'mountain_bikes',
            'gravel_cross_bikes'
        ]

        result = self._scraper._get_categories()
        print('\nCategories:', result)
        self.assertTrue(len(result) > 0, msg='No results returned!')
        for key in result.keys():
            self.assertTrue(key in categories,
                            msg=f'{key} is not in {categories}!')

    def test_get_prods_listings(self):
        bike_cats = self._scraper._get_categories()
        for subtype, href in bike_cats[self._bike_type].items():
            soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
                endpoint=href), 'lxml')
            self._scraper._get_prods_on_current_listings_page(
                soup, self._bike_type, subtype)

        # Verify product listings fetch
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 5,
                        msg=f'There are {num_prods} product first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'giant_prods_all.csv')
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
