# python modules
import os
import unittest

from bs4 import BeautifulSoup

# package modules
from scrapers.canyon import Canyon
from utils.unit_test_utils import DATA_PATH, TIMESTAMP


class CanyonTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Canyon(save_data_path=DATA_PATH)
        self._bike_type = 'mountain'

    def test_get_bike_type_models_hrefs(self):
        model_hrefs = self._scraper._get_bike_type_models_hrefs(self._bike_type)
        num_models = len(model_hrefs)
        self.assertTrue(num_models > 0,
                        msg=f'{num_models} number of model hrefs.')
        print(f'\n{self._bike_type} model hrefs\n', model_hrefs)

    def test_get_subtypes(self):
        result = self._scraper._get_subtypes()
        print('Subtypes:\n', result)
        categories = self._scraper._get_categories()

        # verify main cat and model hrefs in correctly in result
        for bike_type, subtypes in result.items():
            for subtype, models in subtypes.items():
                for model, href in models.items():
                    hrefs = categories[bike_type]['hrefs']
                    self.assertTrue(href in hrefs,
                                    msg=f'{href} not in {bike_type}:{hrefs}')

    def test_get_prods_listings(self):
        categories = self._scraper._get_subtypes()
        for subtype, models in categories[self._bike_type].items():
            for href in models.values():
                soup = BeautifulSoup(
                    self._scraper._fetch_prod_listing_view(endpoint=href),
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
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'canyon_prods_all.csv')
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
                    'fork', 'wheel', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
