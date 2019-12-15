# python modules
import unittest
import os
from bs4 import BeautifulSoup
from datetime import datetime

# package modules
from scrapers.wiggle import Wiggle

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
TEST_PROD_LISTING_PATH = os.path.join(TEST_DATA_PATH, 'performance_prod_listing_test_data.csv')
SHOP_BIKES_HTML_PATH = os.path.abspath(os.path.join(HTML_PATH, '_scraper.html'))
KIDDIMOTO_SPECS = {
    'wheel_size': '12" (203)'
    }
ORRO_SPECS = {
    'frame': 'Orro Pyro Carbon Disc Brake Frame',
    'fork': 'Orro Superlight 2.0 Full Carbon Disc Brake',
    'brake_shift_levers': 'Shimano 105 R7000',
    'brakes': 'TRP Spyre mechanical disc brake, flat mount. Shimano Shimano 105 R7000 levers',
    'derailleur': 'Shimano 105 R7000',
    'cassette': 'Shimano 105 R7000, 11-28T',
    'chainset': 'FSA Omega, 50/34T',
    'wheelset': 'Fulcrum Racing 600 DB',
    'tyres': 'Continental Grand Sport Race 25C',
    'fork_material': 'Carbon',
    'bottle_cage_mounts': 'Double',
    'groupset_manufacturer': 'Shimano',
    'chainset_type': 'Double',
    'tires': 'Continental Grand Sport Race 25C',
    'brake_type': 'Hydraulic Disc Brake',
    'bar_tape_grips': 'Token Lock On',
    'handlebars': 'FSA Vero Compact',
    'stem': 'Integrated',
    'seat_post': 'Orro Superlite Alloy',
    'saddle': 'Prologo Kappa RS',
    'model_year': '2019',
    'road': 'Yes'
    }
VITUS_SPECS = {
    'weight': '7.9kg',
    'frame': 'Carbon',
    'fork': 'Carbon',
    'fork_material': 'Carbon',
    'steerer': 'Tapered 1 1/8 - 1 1/2',
    'bottle_cage_mounts': 'Double',
    'cable_routing': 'External',
    'mudguard_mounts': 'Yes',
    'rear_rack_mounts': 'Yes',
    'groupset_manufacturer': 'Shimano',
    'number_of_gears': '22 Speed',
    'chainset': 'Shimano Ultegra',
    'chainset_type': 'Double',
    'chain': 'KMC X11L',
    'cassette': 'Shimano Ultegra',
    'wheel_size': '700c (622)',
    'tires': 'Mavic Yksion Pro',
    'brake_type': 'Hydraulic Disc Brake',
    'brakes': 'Shimano Ultegra R8020',
    'brake_calipers': 'Shimano Ultegra R8020',
    'handlebars': 'Ritchey Comp Streem II',
    'stem': 'Ritchey Comp 4 Axis',
    'seat_post': 'Prime carbon',
    'saddle': 'Fizik Antares R5',
    'model_year': '2018',
    'bike_weight': '7.9kg / 17.41 lbs',
    'road': 'Yes'
    }


class WiggleTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Wiggle(save_data_path=DATA_PATH)

    def test_get_categories(self):
        expected = ['road', 'mountain', 'cyclocross', 'adventure',
                    'touring', 'urban', 'track', 'time_trial',
                    'bmx', 'kids']
        result = self._scraper._get_categories()
        print('\nCategories', result)
        for key in result.keys():
            self.assertTrue(key in expected,
                            msg=f'{key} not in {expected}.')

    def test_get_prods_listings(self):
        bike_type = 'road'
        bike_cats = self._scraper._get_categories()
        endpoint = bike_cats[bike_type]['href']
        soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
            url=endpoint), 'lxml')

        # Verify product listings fetch
        self._scraper._get_prods_on_current_listings_page(soup, bike_type)
        num_prods = len(self._scraper._products)
        expected_num_prods = bike_cats[bike_type]['count']
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
                                      'wiggle_prods_all.csv')
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
                    'fork', 'cassette', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
