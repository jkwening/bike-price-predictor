# python modules
import os
import unittest

from bs4 import BeautifulSoup

# package modules
from scrapers.lynskey import Lynskey
from utils.unit_test_utils import DATA_PATH, TIMESTAMP


class SpecializedTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Lynskey(save_data_path=DATA_PATH)
        self._bike_type = 'gravel'

    def test_get_subtypes(self):
        expected = {
            'road': {
                'road_pro_racing': ['helix_pro', 'r480']
            },
            'gravel': {
                '2020_pro_gr': ['2020_pro_gr'],
                '2020_gr_race': ['2020_gr_race']
            }
        }
        result = self._scraper._get_subtypes()
        print('Subtypes:', result)
        # verify parsing subtypes and models structure correctly
        for bike_type, subtypes in expected.items():
            self.assertTrue(bike_type in result.keys(),
                            msg=f'{bike_type} not in result bike_types.')
            for subtype, models in expected[bike_type].items():
                self.assertTrue(subtype in result[bike_type].keys(),
                                msg=f'{subtype} not in result subtypes.')
                for model in models:
                    self.assertTrue(model in result[bike_type][subtype].keys(),
                                    msg=f'{model} not in result models.')
        # non-bike types should not be included in results
        for bike_type in result.items():
            self.assertTrue(bike_type not in ['clearance', 'parts'],
                            msg=f'{bike_type} should not be in results bike_type.')

    def test_get_prods_listings(self):
        categories = self._scraper._get_subtypes()
        for subtype, models in categories[self._bike_type].items():
            for model, href in models.items():
                soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
                    endpoint=href, base_url=False),
                    'lxml'
                )

                self._scraper._get_prods_on_current_listings_page(
                    soup, self._bike_type, subtype
                )
        # Verify product listings fetch
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 2,
                        msg=f'There are {num_prods} product first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        month, year, day = TIMESTAMP.split('-')
        prods_csv_path = os.path.join(
            DATA_PATH, month, year, day, 'lynskey_prods_all.csv'
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
        expected = ['site', 'product_id', 'tire',
                    'lever_brakeset', 'cassette', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
