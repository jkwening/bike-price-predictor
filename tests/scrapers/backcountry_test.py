# python modules
import unittest
import os

from bs4 import BeautifulSoup

# package modules
from scrapers.backcountry import BackCountry
from utils.unit_test_utils import DATA_PATH, TIMESTAMP


class SpecializedTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = BackCountry(save_data_path=DATA_PATH)
        self._bike_type = 'road_bikes'

    def test_get_categories(self):
        categories = [
            'road_bikes',
            'mountain_bikes',
            'ebikes',
            'gravel_cyclocross_bikes',
            'triathlon_tt_bikes'
        ]

        result = self._scraper._get_categories()
        print('\nCategories:', result)
        self.assertEqual(len(categories), len(result),
                         msg=f'Expected {len(categories)}; result {len(result)}')
        for key in categories:
            self.assertTrue(key in result,
                            msg=f'{key} is not in result!')

    def test_get_subtypes(self):
        bike_type = 'mountain_bikes'
        subtypes = ['trail', 'enduro', 'cross_country', 'downhill',
                    'mud_sand_snow']
        bike_cats = self._scraper._get_categories()
        endpoint = bike_cats[bike_type]['href']
        soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
            endpoint), 'lxml')
        result = self._scraper._get_subtypes(soup)
        print('\nSubtypes:', result)
        self.assertEqual(len(subtypes), len(result),
                         msg=f'Expected {len(subtypes)}; result {len(result)}')
        for key in subtypes:
            self.assertTrue(key in result,
                            msg=f'{key} is not in result!')

    def test_get_prods_listings(self):
        bike_cats = self._scraper._get_categories()
        endpoint = bike_cats[self._bike_type]['href']
        soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
            endpoint), 'lxml')
        sub_types = self._scraper._get_subtypes(soup)
        for sub_type in sub_types:
            endpoint = sub_types[sub_type]
            soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
                endpoint), 'lxml')

            # Verify product listings fetch
            self._scraper._get_prods_on_current_listings_page(soup,
                                                              self._bike_type,
                                                              sub_type)
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 2,
                        msg=f'There are {num_prods} product first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'backcountry_prods_all.csv')
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
        expected = ['site', 'product_id', 'frame_material',
                    'fork', 'cassette', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
