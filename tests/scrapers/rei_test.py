# python modules
import json
import os
import unittest

# package modules
from scrapers.rei import Rei
from utils.unit_test_utils import DATA_PATH, TIMESTAMP


class ReiTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Rei(save_data_path=DATA_PATH)
        self._bike_type = 'specialty'
        self._categories = ['mountain', 'road', 'specialty',
                            'hybrid', 'electric']

    def test_get_categories(self):
        result = self._scraper._get_categories()
        print('\nCategories:', result)
        self.assertEqual(len(self._categories), len(result),
                         msg=f'Expected {len(self._categories)}; result {len(result)}')
        for key in result.keys():
            self.assertTrue(key in self._categories,
                            msg=f'{key} is not in {self._categories}!')

    def test_get_subtypes(self):
        bike_type = 'specialty'
        expected_subtypes = ['cruiser', 'folding', 'cargo']
        result = self._scraper._get_subtypes()
        print('Subtypes:', result)
        self.assertEqual(len(self._categories), len(result))
        for subtype in result[bike_type].keys():
            self.assertTrue(subtype in expected_subtypes,
                            msg=f'{subtype} not in {expected_subtypes}')

    def test_get_prods_listings(self):
        categories = self._scraper._get_subtypes()
        for subtype, values in categories[self._bike_type].items():
            # only need subtype url name not entire endpoint
            bike = values['href'].split('/')[-1]
            data = json.loads(
                self._scraper._fetch_prod_listing_view(
                    page_size=30, bike=bike
                )
            )

            self._scraper._get_prods_on_current_listings_page(
                data, self._bike_type, subtype
            )
        # Verify product listings fetch
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 2,
                        msg=f'There are {num_prods} product first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'rei_prods_all.csv')
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
                    'fork', 'number_of_gears', 'saddle', 'seat_post']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
