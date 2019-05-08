# python modules
import unittest
import os
from datetime import datetime
import json

from bs4 import BeautifulSoup

# package modules
from scrapers.spokes import Spokes

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
    os.path.join(HTML_PATH, 'spokes-bikes.html'))
SPECS1 = {'frame': 'Trek Custom Steel', 'fork': 'SR Suntour M-3030, coil spring, preload, 75mm travel', 'headset': '1-1/8" threadless', 'rims_wheels': 'Bontrager AT-550 36-hole alloy', 'hubs': 'Front: Formula FM21 alloy; Rear: Formula FM31 alloy', 'spokes': 'Bontrager Approved', 'tires': 'Bontrager LT3, 26x2.00"', 'crankset': 'Shimano Tourney M131', 'chainrings': '42/34/24', 'bottom_bracket': 'Sealed cartridge', 'chain': 'KMC Z51', 'front_derailleur': 'Shimano Tourney TY500', 'rear_derailleur': 'Shimano Tourney TY300', 'rear_cogs': 'Shimano TZ21 14-28, 7 speed', 'shifters': 'Shimano Tourney EF40, 7 speed', 'handlebars': 'Bontrager Riser, 25.4mm, 30mm rise', 'tape_grips': 'Bontrager SSR', 'stem': 'Bontrager alloy, 25.4mm, 25 degree', 'brakes': 'Tektro alloy linear-pull', 'pedals': 'Wellgo nylon platform', 'saddle': 'Bontrager SSR', 'seatpost': 'Bontrager SSR, 2-bolt head, 29.2mm, 12mm offset'}
SPECS2 = {'frame': 'Custom Drawn 6000 Series Aluminum', 'fork': 'Hi-Tensile Steel', 'rims_wheels': '26" double-wall 32H alloy rims', 'hubs': 'QR disc hubs, freewheel rear', 'tires': '26 x 2.125"', 'crankset': 'Alloy, 170mm w/ Chainguard', 'chainrings': '42T', 'rear_derailleur': 'Shimano Altus', 'cassette_rear_cogs': 'Shimano 13-24T 8-Speed', 'shifters': 'Shimano Altus 8-Spd Push Button', 'handlebars': 'EVO Cruiser 122 x 630mm', 'tape_grips': 'EVO Ergonomic 85mm', 'stem': 'EVO 80 Degree', 'brakes': 'Mechanical Disc, 160/140mm rotors', 'pedals': 'Rubber Cage w/ Alloy Body 9/16"', 'saddle': 'EVO Cruiser', 'seat_post': 'EVO 27.2 x 300mm', 'accessories_extras': 'Center mount kickstand, chainguard'}
SPECS3 = {'drive_system': 'Promovec 250W, 36V front hub', 'display': 'Promovec bar-mounted LED with walk-assist', 'battery_type_weight': 'Promovec 36V, 7.8Ah Li-ION smart battery', 'recharge_time': '4 hours', 'max__assisted_speed': '20 mph', 'range': '50 miles', 'frame': 'Premium reinforced eBike aluminum', 'fork': 'Full chromoly', 'headset': 'Threaded', 'rims_wheels': '700c, Alex DH19 double wall', 'hubs': 'Promovec front, Alloy rear', 'tires': 'Kenda, 700 x 40c', 'crankset': 'Prowheel 170mm', 'chainrings': '44T', 'rear_derailleur': 'Shimano Tourney TY-500', 'cassette_rear_cogs': 'Shimano TZ21, 7-speed, 14-28T', 'shifters': 'MicroShift Twist Shifter', 'handlebars': 'Alloy riser, 660mm', 'tape_grips': 'Comfort, 135/92mm', 'stem': 'Promax adjustable', 'brakes': 'Tektro 855AL v-brakes', 'pedals': 'Polished alloy with rubber tread', 'saddle': 'SR Freeway', 'seatpost': 'Alloy 27.2 x 300mm', 'accessories_extras': 'Rear mounted rack for battery, heavy-duty center mount kickstand'}


class CityBikesTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Spokes(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = {
            'road_bikes': {'filter_par': 'rb_ct', 'filter_val': 1001,
                           'href': '/product-list/bikes-1000/?rb_ct=1001', 'count': 307},
            'mountain_bikes': {'filter_par': 'rb_ct', 'filter_val': 1006,
                               'href': '/product-list/bikes-1000/?rb_ct=1006', 'count': 296},
            'cyclocross': {'filter_par': 'rb_ct', 'filter_val': 1014,
                           'href': '/product-list/bikes-1000/?rb_ct=1014', 'count': 56},
            'commuter_urban': {'filter_par': 'rb_ct', 'filter_val': 1017,
                               'href': '/product-list/bikes-1000/?rb_ct=1017', 'count': 162},
            'comfort': {'filter_par': 'rb_ct', 'filter_val': 1020,
                        'href': '/product-list/bikes-1000/?rb_ct=1020', 'count': 53},
            'cruiser': {'filter_par': 'rb_ct', 'filter_val': 1021,
                        'href': '/product-list/bikes-1000/?rb_ct=1021', 'count': 44},
            'fitness': {'filter_par': 'rb_ct', 'filter_val': 1250,
                        'href': '/product-list/bikes-1000/?rb_ct=1250', 'count': 97},
            'electric': {'filter_par': 'rb_ct', 'filter_val': 1038,
                         'href': '/product-list/bikes-1000/?rb_ct=1038', 'count': 65},
            'hybrid_bike': {'filter_par': 'rb_ct', 'filter_val': 1022,
                            'href': '/product-list/bikes-1000/?rb_ct=1022', 'count': 120},
            'childrens': {'filter_par': 'rb_ct', 'filter_val': 1023,
                          'href': '/product-list/bikes-1000/?rb_ct=1023', 'count': 63},
            'bmx': {'filter_par': 'rb_ct', 'filter_val': 1032,
                    'href': '/product-list/bikes-1000/?rb_ct=1032', 'count': 4},
            'other': {'filter_par': 'rb_ct', 'filter_val': 1037,
                      'href': '/product-list/bikes-1000/?rb_ct=1037', 'count': 9}}

        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result = self._scraper._get_categories(soup)

        for title in categories.keys():
            cat = categories[title]
            r_cat = result[title]
            for key in cat.keys():
                self.assertTrue(cat[key] == r_cat[key],
                                msg=f'{title}-{key}: result={r_cat[key]} - '
                                    f'expected:'
                                    f'{cat[key]}')

    def test_get_prod_listings(self):
        with open(SHOP_BIKES_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        self._scraper._get_prods_on_current_listings_page(
            soup, 'commuter_urban')
        self.assertEqual(30, len(self._scraper._products),
                         msg='First page should return 30 products.')

    def test_get_all_available_prods(self):
        self._scraper.get_all_available_prods()

        total_bikes = 0
        for values in self._scraper._BIKE_CATEGORIES.values():
            total_bikes += values['count']
        num_prods = len(self._scraper._products)
        # There are dupes so expect less num_prods
        self.assertTrue(total_bikes >= num_prods,
                        msg=f'expected: {total_bikes} - found: {num_prods}')

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'spokes-trek.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text1 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'spokes-seabrook.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text2 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'spokes-fitzroy.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text3 = f.read()

        soup1 = BeautifulSoup(
            prod_detail_text1, 'lxml')
        soup2 = BeautifulSoup(
            prod_detail_text2, 'lxml')
        soup3 = BeautifulSoup(prod_detail_text3, 'lxml')

        # case 1: exact match per example data
        result = self._scraper._parse_prod_specs(soup1)
        self.assertEqual(len(SPECS1), len(result))
        for key in SPECS1.keys():
            self.assertEqual(
                SPECS1[key], result[key])

        # case 2: using second data, exact match in components
        result = self._scraper._parse_prod_specs(soup2)
        self.assertEqual(len(SPECS2), len(result))
        for key in SPECS2.keys():
            self.assertEqual(SPECS2[key], result[key])

        # case 3: safely handle missing specs
        result = self._scraper._parse_prod_specs(soup3)
        self.assertEqual(len(SPECS3), len(result))
        for key in SPECS3.keys():
            self.assertEqual(SPECS3[key], result[key])


if __name__ == '__main__':
    unittest.main()
