# python modules
import os
import unittest

from bs4 import BeautifulSoup

# package modules
from scrapers.bicycle_warehouse import BicycleWarehouse
from utils.unit_test_utils import DATA_PATH, TIMESTAMP


class BicycleWarehouseTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = BicycleWarehouse(save_data_path=DATA_PATH)
        self._bike_type = 'road_bikes'
        self._categories = [
            'road_bikes',
            'mountain_bikes',
            'path_pavement'
        ]

    def test_get_categories(self):
        result = self._scraper._get_categories()
        print('\nCategories:', result)
        self.assertEqual(len(self._categories), len(result),
                         msg=f'Expected {len(self._categories)}; result {len(result)}')
        for key in result:
            self.assertTrue(key in self._categories,
                            msg=f'{key} is not in {self._categories}!')

    def test_get_subtypes(self):
        bike_type = 'mountain_bikes'
        mtb_sub_types = [
            'hardtails', 'full_suspension', 'cross_country', 'enduro',
            'electric_mtb', 'fat_bikes', 'trail'
        ]

        result = self._scraper._get_subtypes()
        print('\nSub_types:', result)
        self.assertEqual(len(self._categories), len(result),
                         msg=f'Expected {len(self._categories)}; result {len(result)}')
        for key in result:
            self.assertTrue(key in self._categories,
                            msg=f'{key} is not in {self._categories}!')
        for key in result[bike_type]:
            self.assertTrue(key in mtb_sub_types,
                            msg=f'{key} is not in {mtb_sub_types}!')

    def test_get_prods_listings(self):
        bike_cats = self._scraper._get_subtypes()
        for sub_type, href in bike_cats[self._bike_type].items():
            soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
                endpoint=href), 'lxml')

            self._scraper._get_prods_on_current_listings_page(
                soup, self._bike_type, sub_type
            )
        # Verify product listings fetch
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 5,
                        msg=f'There are {num_prods} product first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'bicycle_warehouse_prods_all.csv')
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
                    'fork', 'crankset', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
