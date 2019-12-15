# python modules
import os
import unittest

from bs4 import BeautifulSoup

# package modules
from scrapers.competitive_cyclist import CompetitiveCyclist
from utils.unit_test_utils import DATA_PATH, TIMESTAMP


class CompetitiveCyclistTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = CompetitiveCyclist(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = [
            'road',
            'mountain',
            'cyclocross',
            'triathlon',
            'ebike',
            'fat',
            'kids',
            'gravel'
        ]

        result = self._scraper._get_categories()
        print('\nCategories:', result)
        self.assertEqual(len(categories), len(result),
                         msg=f'Expected {len(categories)}; result {len(result)}')
        for key in categories:
            self.assertTrue(key in result,
                            msg=f'{key} is not in {result}!')

    def test_get_next_page(self):
        categories = self._scraper._get_categories()

        # case: road's page typically has enough prods for next page button
        href = categories['road']
        soup = BeautifulSoup(
            self._scraper._fetch_prod_listing_view(endpoint=href),
            'lxml'
        )
        result = self._scraper._get_next_page(soup)
        print('\nRoad next page result:', result)
        self.assertTrue(result[0])

        # case: triathlon page typically doesn't have enough prods
        href = categories['triathlon']
        soup = BeautifulSoup(
            self._scraper._fetch_prod_listing_view(endpoint=href),
            'lxml'
        )
        result = self._scraper._get_next_page(soup)
        print('\nTriathlon next page result:', result)
        self.assertFalse(result[0])

    def test_get_prods_listings(self):
        bike_type = 'road'
        bike_cats = self._scraper._get_categories()
        endpoint = bike_cats[bike_type]
        soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
            endpoint), 'lxml')

        # Verify product listings fetch
        self._scraper._get_prods_on_current_listings_page(soup, bike_type)
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 5,
                        msg=f'There are {num_prods} product on first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        bike_type = 'road'
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'competitive_prods_all.csv')
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
        expected = ['site', 'product_id', 'frame_material',
                    'fork', 'cassette', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
