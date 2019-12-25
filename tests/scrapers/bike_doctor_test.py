# python modules
import os
import unittest

from bs4 import BeautifulSoup

# package modules
from scrapers.bike_doctor import BikeDoctor
from utils.unit_test_utils import DATA_PATH, TIMESTAMP


class BikeDoctorTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = BikeDoctor(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = ['road', 'mountain', 'commuter_urban', 'comfort',
                      'fitness', 'hybrid', 'childrens', 'cruiser',
                      'cyclocross', 'dirt_jump', 'bmx']

        result = self._scraper._get_categories()
        print('\nCategories:', result)
        for key in result.keys():
            self.assertTrue(key in categories,
                            msg=f'{key} not in {categories}')

    def test_get_prods_listing(self):
        bike_type = 'road'
        bike_cats = self._scraper._get_categories()
        qs = '&rb_ct=' + str(bike_cats[bike_type]['filter_val'])
        soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
            qs=qs), 'lxml')

        # Verify product listings fetch
        self._scraper._get_prods_on_current_listings_page(soup, bike_type)
        num_prods = len(self._scraper._products)
        expected_num_prods = int(bike_cats[bike_type]['count'])
        if expected_num_prods > self._scraper._page_size:
            self.assertEqual(num_prods, self._scraper._page_size,
                             msg=f'{num_prods} product, expected: {self._scraper._page_size}.')
        else:
            self.assertEqual(expected_num_prods, num_prods,
                             msg=f'{num_prods} product, expected: {expected_num_prods}.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        bike_type = 'road'
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'bike_doctor_prods_all.csv')
        # Verify parsing product specs
        specs = self._scraper.get_product_specs(get_prods_from=prods_csv_path,
                                                bike_type=bike_type,
                                                to_csv=False)
        num_prods = len(self._scraper._products)
        num_specs = len(specs)
        self.assertEqual(num_prods, num_specs,
                         msg=f'Products size: {num_prods}, Specs size: {num_specs}')
        self._scraper._write_prod_specs_to_csv(specs=specs,
                                               bike_type=bike_type)

        # Verify spec fieldnames has minimum general fields:
        expected = ['site', 'product_id', 'frame',
                    'fork', 'cassette_rear_cogs', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
