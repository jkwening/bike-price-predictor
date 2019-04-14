# python modules
import unittest
import os
from datetime import datetime

from bs4 import BeautifulSoup

# package modules
from scrapers.canyon import Canyon

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
SHOP_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'canyon.html'))
STRIVE_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'canyon-strive.html'))
ULTIMATE_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'canyon-ultimate.html'))
WMV_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'canyon-wmn-mtb.html'))
SAMPLE_SPECS1 = {'frame': 'Canyon Pathlite AL', 'fork': 'Suntour NRX-D', 'headset': 'Acros AzX 214', 'rear_derailleur': 'Shimano Deore XT Shadow Plus, 11s', 'front_derailleur': 'Shimano SLX, 11s', 'shifters': 'Shimano SLX, 11s', 'brakes': 'Shimano BR MT201 Flatmount', 'hubs': 'Shimano HB-TX505 | Shimano FH-TX505', 'cassette': 'Shimano SLX, 11s', 'rims': 'Alex MD23', 'tires': 'Maxxis Rambler', 'cranks': 'Shimano Deore XT, 11s', 'chainrings': '28 | 38', 'chain': 'Shimano CN-HG601, 11s', 'bottom_bracket': 'Shimano BB-MT800', 'stem': 'Iridium V23', 'handlebar': 'Canyon H40', 'grips': 'Ergon GS 2', 'saddle': 'Iridium Fitness', 'seat_post': 'Iridium S35', 'pedals': 'VP Components  VP-536'}
SAMPLE_SPECS2 = {'frame': 'Canyon Speedmax CF SLX', 'fork': 'Canyon F32 Aero', 'headset': 'Canyon | Acros', 'rear_derailleur': 'Shimano Dura-Ace DI2, 11s', 'derailleur_hanger': 'Derailleur Hanger No. 41', 'front_derailleur': 'Shimano Dura-Ace DI2, 11s', 'shifters': 'Shimano Dura-Ace Di2, 1 Button', 'brake_levers': 'Shimano Dura-Ace Di2, 11s', 'brakes': 'Canyon B11 | B12 integrated Aero', 'cassette': 'Shimano Dura-Ace, 11s', 'wheelset': 'Zipp 858 NSW', 'tires': 'Continental Grand Prix Attack III | Grand Prix Force III', 'cranks': 'Shimano Dura-Ace, 11s', 'chainrings': '53 | 39', 'chain': 'Shimano CN-HG900-11', 'bottom_bracket': 'Shimano Pressfit', 'stem': 'Canyon V19 AL Aero', 'handlebar': 'Canyon HB48 Basebar CF flat', 'extensions': 'Canyon E192 AL Extensions Ergo-S-Bend', 'grips': 'Ergon Canyon Base Bar Grips', 'saddle': 'Fizik Mistica', 'seat_post': 'Canyon S31 CF', 'seat_clamp': 'Canyon integrated', 'nutrition_systems': 'Canyon Energy Box', 'pedals': 'none included'}
SAMPLE_SPECS3 = {'frame': 'Canyon STRIVE CFR', 'rear_shock': 'RockShox Super Deluxe RTR', 'fork': 'RockShox Lyrik RCT3', 'headset': 'Canyon | Acros', 'rear_derailleur': 'SRAM X01 Eagle, 12s', 'chain_guide': 'e.thirteen TRS+', 'shifters': 'SRAM X01 Eagle Trigger, 12s', 'brakes': 'SRAM Code RSC', 'cassette': 'SRAM XG-1295 Eagle, 12s', 'wheelset': 'Mavic Deemax Pro', 'tires': 'Maxxis Minion DHR II 2.4', 'cranks': 'SRAM X01 EAGLE Carbon, 12s', 'chainrings': '32', 'chain': 'SRAM GX Eagle', 'bottom_bracket': 'SRAM DUB BSA', 'stem': 'Canyon G5', 'handlebar': 'Canyon G5 CARBON', 'grips': 'Ergon GD1', 'saddle': 'Ergon SMD20', 'seat_post': 'RockShox Reverb Stealth B1', 'seat_clamp': 'Canyon Race Clamp', 'pedals': 'none included'}


class CanyonTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Canyon(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = [
            'road',
            'mtb',
            'fitness',
            'triathlon',
            'gravity',
            'urban'
        ]

        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result = self._scraper._get_categories(soup)
        print('categories:', result)
        self.assertEqual(len(categories), len(result),
                         msg=f'Expected size: {len(categories)}; result size: {len(result)}')
        for key in categories:
            self.assertTrue(key in result,
                            msg=f'{key} is not in result!')

    def test_get_prod_listings(self):
        # Case 1
        expected = 4
        with open(STRIVE_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        self._scraper._get_prods_on_current_listings_page(
            soup, bike_type='mtb')
        num_bikes = len(self._scraper._products)
        self.assertEqual(expected, num_bikes,
                         msg=f'Expected: {expected}; parsed: {num_bikes}')

        # Case 2
        expected += 4
        with open(WMV_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        self._scraper._get_prods_on_current_listings_page(
            soup, bike_type='mtb')
        num_bikes = len(self._scraper._products)
        self.assertEqual(expected, num_bikes,
                         msg=f'Expected: {expected}; parsed: {num_bikes}')

        # Case 3 - Raise Attribute Error
        with open(ULTIMATE_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        # self._scraper._get_prods_on_current_listings_page(
        #     soup, bike_type='road')
        self.assertRaises(AttributeError, self._scraper._get_prods_on_current_listings_page,
                          soup, 'road')

    def test_get_all_available_prods(self):
        expected = 15
        # Validate method
        self._scraper.get_all_available_prods()
        num_prods = len(self._scraper._products)
        # There are dupes so expect less num_prods
        self.assertTrue(num_prods > expected,
                        msg=f'expected at least: {expected} - found: {num_prods}')

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'canyon-fitness.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text1 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'canyon-triathlon.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text2 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'canyon-mtb.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text3 = f.read()

        detail_soup1 = BeautifulSoup(
            prod_detail_text1, 'lxml')
        detail_soup2 = BeautifulSoup(
            prod_detail_text2, 'lxml')
        detail_soup3 = BeautifulSoup(
            prod_detail_text3, 'lxml'
        )

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
