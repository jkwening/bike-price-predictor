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
        self._categories = ['road_bikes', 'mountain_bikes', 'commuter_urban', 'comfort',
                            'fitness', 'hybrid_bike', 'cruiser', 'cyclocross',
                            'other']
        self._page_size = 30

    def test_get_categories(self):
        result = self._scraper._get_categories()
        print('\nCategories:', result)
        for key in result.keys():
            self.assertTrue(key in self._categories,
                            msg=f'{key} not in {self._categories}')

    def test_get_subtypes(self):
        bike_type = 'mountain_bikes'
        mtb_subtypes = [
            'hardtail', 'full_suspension', '29_inch_wheel_29ers', '650b_wheel',
            'downhill_freeride', 'fat_bikes', 'rigid', '29_inch_plus_wheel',
            '27_5_inch_plus_wheel', '26_inch_wheel', 'dirt_jump'
        ]
        fitness_subtypes = ['fitness']

        result = self._scraper._get_subtypes()
        print('\nSub_types:', result)
        self.assertEqual(len(self._categories), len(result),
                         msg=f'Expected {len(self._categories)};\
                          result {len(result)}')
        for key in self._categories:
            self.assertTrue(key in result,
                            msg=f'{key} is not in {result}!')
        for key in result[bike_type]:
            self.assertTrue(key in mtb_subtypes,
                            msg=f'{key} is not in {mtb_subtypes}!')
        for key in result['fitness']:
            self.assertTrue(key in fitness_subtypes,
                            msg=f'{key} is not in {fitness_subtypes}!')

    def test_get_prods_listing(self):
        categories = self._scraper._get_subtypes()
        subtypes = categories[self._bike_type]
        for subtype in subtypes:
            qs = 'rb_ct=' + str(subtypes[subtype]['filter_val'])
            soup = BeautifulSoup(
                self._scraper._fetch_prod_listing_view(
                    qs=qs, page_size=self._page_size
                ),
                'lxml'
            )
            print(f'Parsing first page for {self._bike_type}: {subtype}...')
            self._scraper._get_prods_on_current_listings_page(soup, self._bike_type,
                                                              subtype)

        # Verify product listings fetch
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 10,
                        msg=f'{num_prods} product, expected at least 10.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        month, year, day = TIMESTAMP.split('-')
        prods_csv_path = os.path.join(
            DATA_PATH, month, year, day, 'spokes_prods_all.csv'
        )
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
