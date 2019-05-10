# python modules
import unittest
import os
from datetime import datetime
from bs4 import BeautifulSoup

# package modules
from scrapers.jenson import Jenson

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
    os.path.join(HTML_PATH, 'jenson-bikes.html'))
SPECS1 = {'frame': 'ARGON 18 NANOTECH TUBING HM5007', 'fork': 'ARGON 18 KR36X CARBON FORK', 'headset': 'FSA 37E + 3D 1" 1/4', 'shifters': 'SHIMANO RS685', 'front_derailleur': 'SHIMANO 105 5800 BRAZE-ON', 'rear_derailleur': 'SHIMANO 105 5800', 'crankset': 'SHIMANO 105 5800 50/34', 'bottom_bracket': 'SHIMANO BB PRESS FIT SM-BB71-41B', 'pedals': '', 'chain': 'FSA TEAM ISSUE 11S', 'cassette': 'SHIMANO 105 5800 11/28', 'brakes': 'SHIMANO RS785 CALIPER, RT-99 140 ROTOR', 'wheelset': 'SHIMANO RX010', 'tires': 'VITTORIA CROSS XN 700X31', 'handlebar': 'FSA OMEGA ALLOY', 'stem': 'FSA OMEGA ALLOY', 'bar_tape': '', 'seatpost': 'ARGON 18 ASP-1600 CARBON 27,2MM', 'seatclamp': 'tba', 'saddle': 'PROLOGO KAPPA EVO', 'intended_use': 'Race, Gravel, Adventure', 'weight': '20 lbs (54cm)'}
SPECS2 = {'frame': 'Reynolds 853 Steel', 'fork': 'RDO Carbon Fork with rack mounts', 'headset': 'Niner integrated IS42/28.6, IS52/40', 'shifters': 'Shimano Tiagra 2x10', 'front_derailleur': 'Shimano Tiagra 4700', 'rear_derailleur': 'Shimano Tiagra 4700', 'crankset': 'Shimano Tiagra RS400 50x34T', 'crank_arm_lengths': '-', 'bottom_bracket': 'Shimano', 'pedals': '-', 'chain': 'Shimano HG54 10-speed', 'cassette': 'Shimano HG500, 11-34T', 'brakes': 'Shimano Tiagra RS405 Hydraulic', 'wheelset': 'Niner CX Alloy, 15x100mm, 12x142mm', 'tires': 'Schwalbe G-One Performance, 700x38c', 'handlebar': 'Easton EA50 AX', 'handlebar_widths': '-', 'stem': 'Niner Alloy Stem', 'stem_lengths': '-', 'bar_tape': 'Niner Bar Tape', 'seatpost': 'Niner Alloy, 400mm', 'seatclamp': '31.8', 'saddle': 'Niner Custom with Chromoly rails', 'intended_use': 'Gravel, Road', 'weight': '-'}
SPECS3 = {}
SPECS4 = {'frame': 'Orbea Gain Carbon', 'fork': 'Gain Carbon flat mount', 'headset': 'FSA 1-1/8 - 1-1/2" Integrated Carbon Cup ACB Bearings', 'shifters': 'Shimano ST-7020', 'front_derailleur': 'Shimano 105 R7000', 'rear_derailleur': 'Shimano 105 R7000 GS', 'crankset': 'Shimano 105 R7000 34x50t', 'crank_arm_lengths': '170mm (47, 51, 53 frame), 172mm (55 frame), 175mm (57 frame)', 'bottom_bracket': 'Shimano', 'pedals': 'N/A', 'chain': 'KMC e11 Turbo Silver', 'cassette': 'Shimano 105 R7000 11-32t 11-Speed', 'brakes': 'Shimano R7070 Hydraulic Disc', 'wheelset': 'Mavic Aksium Elite Disc UST', 'tires': 'Mavic Yksion Pro 700x28 UST', 'handlebar': 'FSA Gossamer Compact', 'handlebar_widths': '380mm (47 frame), 420mm (51, 53 frame), 440mm (55, 57 frame)', 'stem': 'Orbea OC-III', 'stem_lengths': '90mm (47 frame), 100mm (51, 53 frame), 110mm (55, 57 frame)', 'bar_tape': 'Anti-Slip/Shock Proof Bar Tape, Black', 'seatpost': 'Orbea OC-III Carbon 31.6x350mm', 'seatclamp': 'Orbea bolt-on', 'saddle': 'Prologo Kappa Space STN size 147mm', 'intended_use': 'Road', 'weight': 'N/A'}


class CityBikesTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Jenson(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = {
            'mountain_bikes': {'href': '/Mountain-Bikes'},
            'road_bikes': {'href': '/Road-Bikes'},
            'cyclocross_gravel_bikes': {'href': '/Cyclocross-Gravel-Bikes'},
            # 'jenson_usa_exclusive_builds': {'href': '/Jenson-USA-Exclusive-Builds'},
            'electric_bikes': {'href': '/Electric-Bikes'},
            'commuter_urban_bikes': {'href': '/Commuter-Urban-Bikes'},
            'bmx_bikes': {'href': '/BMX-Bikes'},
            'kids_bikes': {'href': '/Kids-Bikes'},
            'corona_store_exclusives': {'href': '/Corona-Store-Exclusives'},
            # 'bikes_on_sale': {'href': '/Sale/Complete-Bikes'}
        }

        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result = self._scraper._get_categories(soup)
        print(result)
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
        self.assertEqual(24, len(self._scraper._products),
                         msg='First page should return 24 products.')

    def test_get_all_available_prods(self):
        self._scraper.get_all_available_prods()

        expected = 400
        num_prods = len(self._scraper._products)
        # There are dupes so expect less num_prods
        self.assertTrue(expected >= num_prods,
                        msg=f'Expected: {expected} - found: {num_prods}')

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'jenson-evil.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text1 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'jenson-rlt.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text2 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'jenson-lafree.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text3 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'jenson-obea.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text4 = f.read()

        soup1 = BeautifulSoup(
            prod_detail_text1, 'lxml')
        soup2 = BeautifulSoup(
            prod_detail_text2, 'lxml')
        soup3 = BeautifulSoup(prod_detail_text3, 'lxml')
        soup4 = BeautifulSoup(prod_detail_text4, 'lxml')

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

        # case 4: multiple specs table
        result = self._scraper._parse_prod_specs(soup4)
        self.assertEqual(len(SPECS4), len(result))
        for key in SPECS4.keys():
            self.assertEqual(SPECS4[key], result[key])


if __name__ == '__main__':
    unittest.main()
