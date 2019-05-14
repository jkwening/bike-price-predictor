# python modules
import unittest
import os
from datetime import datetime

from bs4 import BeautifulSoup

# package modules
from scrapers.backcountry import BackCountry

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
SHOP_BIKES_HTML_PATH = os.path.abspath(os.path.join(HTML_PATH,
                                                    'backcountry.html'))
SHOP_SALE_HTML_PATH = os.path.abspath(os.path.join(
    HTML_PATH, 'backcountry-sale.html'))
SHOP_NO_NEXT_HTML_PATH = os.path.abspath(os.path.join(
    HTML_PATH, 'backcountry-tt.html'))
SAMPLE_SPECS1 = {'frame_material': 'carbon CC', 'suspension': 'VPP', 'rear_shock': 'FOX Float Performance Elite DPX', 'rear_travel': '150mm', 'fork': 'FOX 36 Float Factory', 'front_travel': '150mm', 'headset': 'Cane Creek 40 IS Integrated', 'shifters': 'SRAM X01 Eagle (12-speed)', 'rear_derailleur': 'SRAM X01 Eagle (12-speed)', 'iscg_tabs': 'ISCG-05', 'crankset': 'SRAM X1 Eagle DUB', 'chainring_sizes': '30t', 'crank_arm_length': '[x-small - small] 170mm, [medium - x-large] 175mm', 'bottom_bracket': 'SRAM DUB', 'bottom_bracket_type': 'BSA threaded', 'cassette': 'SRAM XG1295 Eagle (12-speed)', 'cassette_range': '10 - 50t', 'chain': 'SRAM X01 Eagle (12-speed)', 'brakeset': 'SRAM Code RSC', 'brake_type': 'hydraulic disc', 'rotors': '[front] 200mm Avid Centerline, [rear] 180mm Avid Centerline', 'handlebar': 'SCB AM Carbon', 'grips': 'Santa Cruz Palmdale', 'stem': 'Race Face Aeffect R', 'stem_length': '50mm', 'saddle': 'WTB Silverado Team', 'seatpost': 'RockShox Reverb Stealth', 'wheelset': 'Santa Cruz Reserve 30 Carbon', 'hubs': 'DT Swiss 350', 'front_axle': '15mm Boost', 'rear_axle': '12 x 148mm', 'tires': '[front] Maxxis Minion DHR II 3C Silkshield, [rear] Maxxis Minion DHR II 3C Silkshield', 'tire_size': '29 x 2.4in', 'pedals': 'not included', 'claimed_weight': '28lb 11oz', 'recommended_use': 'enduro, trail', 'manufacturer_warranty': 'lifetime on frame'}
SAMPLE_SPECS2 = {'frame_material': '24-30t Unidirectional Carbon, Fast Technology', 'fork': 'Dean Aero', 'shifters': 'Shimano 105', 'front_derailleur': 'Shimano 105', 'rear_derailleur': 'Shimano 105', 'crankset': 'FSA Omega', 'chainring_sizes': '52 - 36t', 'bottom_bracket': 'PF30', 'cassette': 'Shimano 105', 'cassette_range': '11 - 30t', 'chain': 'KMC 11-speed', 'brakeset': 'Forza Stratos', 'brake_type': 'rim', 'handlebar': 'Deda Cronoero', 'stem': 'Deda Cronoero', 'seatpost': 'Dean Aero Seatpost', 'wheelset': 'Forza RC31', 'tires': 'Vittoria Zaffiro', 'recommended_use': 'triathlon', 'manufacturer_warranty': '5 years on frame'}
SAMPLE_SPECS3 = {'frame_material': 'titanium', 'fork': 'ENVE', 'fork_material': 'carbon fiber', 'headset': 'Cane Creek', 'shifters': 'Shimano Ultegra Di2 R8050', 'front_derailleur': 'Shimano Ultegra Di2 R8050', 'rear_derailleur': 'Shimano Ultegra Di2 R8050', 'crankset': 'Shimano Ultegra R8000', 'bottom_bracket': 'Shimano Ultegra BB72-41B PressFit', 'crank_arm_length': '[52cm] 170mm, [54 - 56cm] 172.5mm, [58 - 60cm] 175mm', 'cassette': '11 - 25t Shimano Ultegra R8000', 'chain': 'Shimano CN-HG701', 'brakeset': 'Shimano Ultegra R8000', 'brake_type': 'rim', 'handlebar': 'Zipp Service Course', 'handlebar_width': '[52cm] 40cm, [56 - 58cm] 100mm, [60cm] 110mm', 'bar_tape': 'PRO Classic', 'stem': 'Zipp Service Course', 'stem_length': '[52 - 54cm] 90mm, [54 - 56cm] 42cm, [58 - 60cm] 44cm', 'saddle': 'Fizik Aliante R7', 'seatpost': 'Zipp Service Course', 'wheelset': 'Mavic Ksyrium Elite UST', 'hubs': 'Mavic Instant Drive 360', 'front_axle': '9mm quick-release', 'rear_axle': '130mm quick-release', 'skewers': 'Mavic BR301', 'tires': 'Mavic Yksion', 'tire_size': '700c x 25mm', 'pedals': 'not included', 'recommended_use': 'road cycling'}


class SpecializedTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = BackCountry(save_data_path=DATA_PATH)

    def test_get_max_num_prods(self):
        expected = 489
        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        num_prods = self._scraper._get_max_num_prods(soup)
        self.assertEqual(expected, num_prods,
                         msg=f'Expected: {expected}; result: {num_prods}')

    def test_get_categories(self):
        categories = [
            'road_bikes',
            'mountain_bikes',
            'ebikes',
            # 'kids_bikes',
            'gravel_cyclocross_bikes',
            'triathlon_tt_bikes'
        ]

        # Case 1: saved html
        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result = self._scraper._get_categories(soup)
        print('html categories:', result)
        self.assertEqual(len(categories), len(result),
                         msg=f'Expected {len(categories)}; result {len(result)}')
        for key in categories:
            self.assertTrue(key in result,
                            msg=f'{key} is not in result!')

        # Case 2: api call
        result = self._scraper._get_categories(soup=None)
        print('api categories:', result)
        self.assertEqual(len(categories), len(result),
                         msg=f'Expected {len(categories)}; result {len(result)}')
        for key in categories:
            self.assertTrue(key in result,
                            msg=f'{key} is not in result!')

    def test_get_next_page(self):
        # Case 1: next page button exists
        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result = self._scraper._get_next_page(soup)
        self.assertTrue(result[0],
                        msg=f'Expected next page endpoint! Result: {result}')

        # Case 2: no next page button
        with open(SHOP_NO_NEXT_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result = self._scraper._get_next_page(soup)
        self.assertFalse(result[0],
                         msg=f'Expected no next page endpoint! Result: {result}')

    def test_get_prod_listings(self):
        expected = 40
        with open(SHOP_SALE_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        self._scraper._get_prods_on_current_listings_page(
            soup, bike_type='road')
        num_bikes = len(self._scraper._products)
        self.assertEqual(num_bikes, expected,
                         msg=f'Expected: {expected}; parsed: {num_bikes}')

    def test_get_all_available_prods(self):
        expected = 24 * 5
        # Validate method
        self._scraper.get_all_available_prods()
        num_prods = len(self._scraper._products)
        # There are dupes so expect less num_prods
        self.assertTrue(num_prods > expected,
                        msg=f'expected: {expected} - found: {num_prods}')

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'backcountry-hightower.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text1 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'backcountry-ridley.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text2 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'backcountry-alchemy.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text3 = f.read()

        detail_soup1 = BeautifulSoup(prod_detail_text1, 'lxml')
        detail_soup2 = BeautifulSoup(prod_detail_text2, 'lxml')
        detail_soup3 = BeautifulSoup(prod_detail_text3, 'lxml')

        # case 1: exact match per example data
        result = self._scraper._parse_prod_specs(detail_soup1)
        self.assertEqual(len(SAMPLE_SPECS1), len(result))
        for key in SAMPLE_SPECS1.keys():
            self.assertEqual(
                SAMPLE_SPECS1[key], result[key])

        # case 2: using second data, exact match in components
        result = self._scraper._parse_prod_specs(detail_soup2)
        self.assertEqual(len(SAMPLE_SPECS2), len(result))
        for key in SAMPLE_SPECS2.keys():
            self.assertEqual(SAMPLE_SPECS2[key], result[key])

        # case 3: using third data, exact match in components
        result = self._scraper._parse_prod_specs(detail_soup3)
        self.assertEqual(len(SAMPLE_SPECS3), len(result))
        for key in SAMPLE_SPECS3.keys():
            self.assertEqual(SAMPLE_SPECS3[key], result[key],
                             msg=f'{key}: Expected - {SAMPLE_SPECS3[key]}; '
                             f'Result - {result[key]}')


if __name__ == '__main__':
    unittest.main()
