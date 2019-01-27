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
        self._proshop = Proshop(save_data_path=DATA_PATH)

    def test_fetch_prod_listing_view(self):
        text = self._proshop._fetch_prod_listing_view(
            endpoint=self._proshop._PROD_PAGE_ENDPOINT, page_size=30)
        soup = BeautifulSoup(text, 'lxml')
        self._proshop._get_prods_on_current_listings_page(
            soup, bike_type='all')
        self.assertEqual(30, len(self._proshop._products),
                         msg='First page should return 30 products.')

    def test_get_categories(self):
        categories = {
            'road': {'filter_par': 'rb_ct', 'filter_val': 1001, 'count': 256},
            'mountain': {'filter_par': 'rb_ct', 'filter_val': 1006, 'count':
                446},
            'commuter_urban': {'filter_par': 'rb_ct', 'filter_val': 1017,
                               'count': 143},
            'cyclocross': {'filter_par': 'rb_ct', 'filter_val': 1014,
                               'count': 49},
            'comfort': {'filter_par': 'rb_ct', 'filter_val': 1020, 'count':
                26},
            'fitness': {'filter_par': 'rb_ct', 'filter_val': 1902, 'count':
                90},
            'hybrid': {'filter_par': 'rb_ct', 'filter_val': 1022, 'count':
                113},
            'childrens': {'filter_par': 'rb_ct', 'filter_val': 1023, 'count':
                48},
            'other': {'filter_par': 'rb_ct', 'filter_val': 1037, 'count':
                34},
            'bmx': {'filter_par': 'rb_ct', 'filter_val': 1032,
                               'count': 10}
        }

        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result = self._proshop._get_categories(soup)
        for title in categories.keys():
            cat = categories[title]
            r_cat = result[title]
            for key in cat.keys():
                self.assertTrue(cat[key] == r_cat[key],
                                msg=f'{title}-{key}: result={r_cat[key]} - '
                                    f'expected:'
                                    f'{cat[key]}')

    def test_get_prod_listings(self):
        with open(MOUNTAIN_BIKES_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        self._proshop._get_prods_on_current_listings_page(
            soup, 'mountain')
        self.assertEqual(30, len(self._proshop._products),
                         msg='First page should return 3pro0 products.')

    def test_get_all_available_prods(self):
        result = self._proshop.get_all_available_prods()

        total_bikes = 0
        for values in self._proshop._BIKE_CATEGORIES.values():
            total_bikes += values['count']
        num_prods = len(self._proshop._products)
        # There are dupes so expect less num_prods
        self.assertTrue(total_bikes >= num_prods,
                        msg=f'expected: {total_bikes} - found: {num_prods}')

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'proshop-surly.html'))
        with open(html_path, encoding='utf-8') as f:
            surly_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'proshop-specialized-sirrus.html'))
        with open(html_path, encoding='utf-8') as f:
            sirrus_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'proshop-strider.html'))
        with open(html_path, encoding='utf-8') as f:
            generic_error = f.read()

        surly_detail_soup = BeautifulSoup(
            surly_prod_detail_text, 'lxml')
        sirrus_detail_soup = BeautifulSoup(
            sirrus_prod_detail_text, 'lxml')
        generic_error_soup = BeautifulSoup(generic_error, 'lxml')

        # case 1: exact match per example data
        result = self._proshop._parse_prod_specs(surly_detail_soup)
        self.assertEqual(len(SURLY_SPECS), len(result))
        for key in SURLY_SPECS.keys():
            self.assertEqual(
                SURLY_SPECS[key], result[key])

        # case 2: using second data, exact match in components
        result = self._proshop._parse_prod_specs(sirrus_detail_soup)
        self.assertEqual(len(SIRRUS_SPECS), len(result))
        for key in SIRRUS_SPECS.keys():
            self.assertEqual(SIRRUS_SPECS[key], result[key])

        # case 3: safely handle missing specs
        result = self._proshop._parse_prod_specs(generic_error_soup)
        self.assertEqual(0, len(result))


if __name__ == '__main__':
    unittest.main()
