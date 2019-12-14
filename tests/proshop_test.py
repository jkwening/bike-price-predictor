# python modules
import unittest
import os
from datetime import datetime
import json

from bs4 import BeautifulSoup

# package modules
from scrapers.proshop import Proshop

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
SHOP_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'proshop.html'))
MOUNTAIN_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'proshop-mountain.html')
)
SIRRUS_SPECS = {
    'frame': 'Specialized A1 Premium aluminum',
    'fork': 'Specialized steel',
    'rims_wheels': 'Aluminum, double-wall',
    'hubs': 'Aluminum, sealed',
    'spokes': '14-gauge, stainless-steel',
    'tires': 'Specialized Nimbus, 700 x 32c w/Flak Jacket puncture protection',
    'crankset': 'Specialized Stout',
    'chainrings': '48/38/28',
    'front_derailleur': 'Shimano',
    'rear_derailleur': 'Shimano Altus',
    'rear_cogs': 'Shimano, 8-speed: 11-32',
    'shifters': 'Shimano',
    'handlebars': 'Specialized flat, aluminum',
    'tape_grips': 'Specialized Body Geometry Targa',
    'stem': 'Aluminum',
    'brakes': 'V-Brake',
    'pedals': 'Platform',
    'saddle': 'Specialized Canopy Sport',
    'seatpost': 'Aluminum'}
SURLY_SPECS = {
    'frame': 'Surly 4130 chromoly steel; custom double-butted, externally flared tubing; horizontal slotted with derailleur hanger; Surly “Gnot Boost” 142 or 148mm hub spacing compatibility',
    'fork': '4130 chromoly, 483mm axle-to-crown x 47mm offset, 110mm hub spacing, tapered and butted straight blade, 51mm I.S. disc mount',
    'headset': 'Cane Creek',
    'axles': 'Front: 110 x 15mm TA',
    'rims_wheels': 'Alex MD40',
    'hubs': 'Salsa 32h',
    'tires': 'Surly Dirt Wizard 29 x 3, 60 tpi',
    'crankset': 'SRAM NX',
    'chainrings': '30T',
    'bottom_bracket': 'SRAM',
    'chain': 'KMX X11-1',
    'rear_derailleur': 'SRAM NX',
    'cassette_rear_cogs': 'Sun Race, 11-speed: 11-42',
    'shifters': 'SRAM NX',
    'handlebars': 'Answer Pro Taper, 31.8mm',
    'stem': 'H.L. 4-bolt',
    'brake_levers': 'SRAM Level',
    'brakes': 'SRAM Level hydraulic disc, 180mm rotors',
    'saddle': 'WTB Volt Sport',
    'seat_post': 'H.L. 30.9mm'}


class ProshopTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Proshop(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = [
            'road',
            'mountain',
            'cyclocross',
            'commuter_urban',
            'comfort',
            'fitness',
            'hybrid',
            'childrens',
            'other',
            'bmx',
            'cruiser'
        ]

        result = self._scraper._get_categories()
        print('\nCategories:', result)
        for key in result.keys():
            self.assertTrue(key in categories,
                            msg=f'{key} not in {result}')

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
                                      'proshop_prods_all.csv')
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
