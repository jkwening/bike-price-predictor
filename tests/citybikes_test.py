# python modules
import unittest
import os
from datetime import datetime
import json

from bs4 import BeautifulSoup

# package modules
from scrapers.citybikes import CityBikes

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
TEST_PROD_LISTING_PATH = os.path.join(TEST_DATA_PATH,
                                      'performance_prod_listing_test_data.csv')
SHOP_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'citybikes.html'))
COMMUTER_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'citybikes-Commuter_Urban.html')
)
DRAGONFLY_SPECS = {
    'frame': 'Reynolds 853 chromoly, w/dropper post routing, ISCG05, sliding 12x142mm dropouts',
    'fork': 'Fox 32 Float Performance Series, 120mm-travel w/tapered steerer, 15mm thru-axle',
    'rims_wheels': 'WTB Frequency Team i23 TCS',
    'hubs': 'Formula disc',
    'spokes': 'Stainless-steel',
    'tires': 'Vittoria Barzo, 27.5 x 2.25',
    'crankset': 'Shimano',
    'chainrings': '36/22',
    'front_derailleur': 'Shimano Deore',
    'rear_derailleur': 'Shimano SLX Shadow',
    'rear_cogs': 'Shimano, 10-speed: 11-36',
    'shifters': 'Shimano SLX',
    'handlebars': 'Ritchey Trail',
    'tape_grips': 'Jamis lock-on',
    'stem': 'Ritchey Trail',
    'brakes': 'Shimano Deore disc, 180/160mm rotors',
    'saddle': 'WTB Volt Comp w/Luxe Zone Cut-Out',
    'seatpost': 'Ritchey Trail'}
CROSS_TRAIL_SPECS = {
    'frame': 'Specialized A1 Premium Aluminum, Fitness Geometry, butted tubing, rack mounts, Plug + Play fender mounts',
    'fork': 'SR Suntour NEX w/ Specialized Fitness Brain technology, 55mm of travel, 1-1/8" steerer, QR, fender mounts',
    'rims_wheels': '700C disc, double wall',
    'tires': 'Trigger Sport Reflect, 60 TPI, wire bead, 700x38mm',
    'crankset': 'Shimano Tourney, 3-piece',
    'chainrings': '48/38/28T',
    'bottom_bracket': 'BSA, 68mm, square taper',
    'chain': 'KMC X8EPT, 8-speed, anti-corrosion coating w/ reusable Missing Link',
    'front_derailleur': 'Shimano Tourney, top swing, 31.8mm clamp',
    'rear_derailleur': 'Shimano Altus, 8-Speed',
    'cassette_rear_cogs': 'Sunrace, 8-speed, 11-34t',
    'shifters': 'Shimano Altus, RapidFire Plus, w/ gear display',
    'handlebars': 'Double-butted alloy, 9-degree backsweep, 31.8mm',
    'tape_grips': 'Specialized Body Geometry XCT, lock-on',
    'stem': '3D forged alloy, 7-degree rise, 31.8mm clamp',
    'brakes': 'Promax Solve, hydraulic disc, post mount, 160mm rotor',
    'saddle': 'Specialized Canopy Comp, hollow Cr-Mo rails, 155mm',
    'seat_post': 'Alloy, 12mm offset, 2-bolt clamp, 27.2mm'}


class CityBikesTestCase(unittest.TestCase):
    def setUp(self):
        self._citybikes = CityBikes(save_data_path=DATA_PATH)

    def test_fetch_prod_listing_view(self):
        text = self._citybikes._fetch_prod_listing_view(
            endpoint=self._citybikes._PROD_PAGE_ENDPOINT, page_size=30)
        soup = BeautifulSoup(text, 'lxml')
        self._citybikes._get_prods_on_current_listings_page(
            soup, bike_type='all')
        self.assertEqual(30, len(self._citybikes._products),
                         msg='First page should return 30 products.')

    def test_get_categories(self):
        categories = {
            'road': {'filter_par': 'rb_ct', 'filter_val': 1001, 'count': 24},
            'mountain': {'filter_par': 'rb_ct', 'filter_val': 1006, 'count':
                19},
            'commuter_urban': {'filter_par': 'rb_ct', 'filter_val': 1017,
                               'count': 65},
            'comfort': {'filter_par': 'rb_ct', 'filter_val': 1020, 'count':
                13},
            'cruiser': {'filter_par': 'rb_ct', 'filter_val': 1021, 'count':
                1},
            'fitness': {'filter_par': 'rb_ct', 'filter_val': 1249, 'count':
                32},
            'hybrid': {'filter_par': 'rb_ct', 'filter_val': 1022, 'count':
                40},
            'childrens': {'filter_par': 'rb_ct', 'filter_val': 1023, 'count':
                20},
            'other': {'filter_par': 'rb_ct', 'filter_val': 1037, 'count':
                28}
        }

        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result = self._citybikes._get_categories(soup)
        for title in categories.keys():
            cat = categories[title]
            r_cat = result[title]
            for key in cat.keys():
                self.assertTrue(cat[key] == r_cat[key],
                                msg=f'{title}-{key}: result={r_cat[key]} - '
                                    f'expected:'
                                    f'{cat[key]}')

    def test_get_prod_listings(self):
        with open(COMMUTER_BIKES_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        self._citybikes._get_prods_on_current_listings_page(
            soup, 'commuter_urban')
        self.assertEqual(30, len(self._citybikes._products),
                         msg='First page should return 60 products.')

    def test_get_all_available_prods(self):
        result = self._citybikes.get_all_available_prods()

        total_bikes = 0
        for values in self._citybikes._BIKE_CATEGORIES.values():
            total_bikes += values['count']
        num_prods = len(self._citybikes._products)
        # There are dupes so expect less num_prods
        self.assertTrue(total_bikes >= num_prods,
                        msg=f'expected: {total_bikes} - found: {num_prods}')

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'citybikes-Specialized-CrossTrail-Hydraulic-Disc.html'))
        with open(html_path, encoding='utf-8') as f:
            cross_trail_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'citybikes-Jamis-Dragonfly-Women.html'))
        with open(html_path, encoding='utf-8') as f:
            dragonfly_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'citybikes-Specialized-Boys-Hotwalk.html'))
        with open(html_path, encoding='utf-8') as f:
            generic_error = f.read()

        cross_trail_detail_soup = BeautifulSoup(
            cross_trail_prod_detail_text, 'lxml')
        dragonfly_detail_soup = BeautifulSoup(
            dragonfly_prod_detail_text, 'lxml')
        generic_error_soup = BeautifulSoup(generic_error, 'lxml')

        # case 1: exact match per example data
        result = self._citybikes._parse_prod_specs(cross_trail_detail_soup)
        self.assertEqual(len(CROSS_TRAIL_SPECS), len(result))
        for key in CROSS_TRAIL_SPECS.keys():
            self.assertEqual(
                CROSS_TRAIL_SPECS[key], result[key])

        # case 2: using second data, exact match in components
        result = self._citybikes._parse_prod_specs(dragonfly_detail_soup)
        self.assertEqual(len(DRAGONFLY_SPECS), len(result))
        for key in DRAGONFLY_SPECS.keys():
            self.assertEqual(DRAGONFLY_SPECS[key], result[key])

        # case 3: safely handle missing specs
        result = self._citybikes._parse_prod_specs(generic_error_soup)
        self.assertEqual(0, len(result))


if __name__ == '__main__':
    unittest.main()
