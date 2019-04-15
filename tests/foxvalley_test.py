# python modules
import unittest
import os
from datetime import datetime

from bs4 import BeautifulSoup

# package modules
from scrapers.foxvalley import FoxValley

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
SHOP_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'foxvalley-bikes.html'))
SHOP_ROAD_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'foxvalley-road-bikes.html'))
SAMPLE_SPECS1 = {'sizes': 'XS, S, M, M/L, L, XL', 'colors': 'Metallic Blue / Black', 'frame': 'Advanced SL-Grade Composite, integrated seatpost, disc', 'fork': 'Advanced SL-Grade Composite, full-composite OverDrive 2 steerer, disc', 'shock': 'N/A', 'handlebar': 'Giant Contact SLR Aero', 'stem': 'Giant Contact SLR Aero', 'seatpost': 'Advanced SL-grade composite, integrated', 'saddle': 'Giant Contact SLR (forward)', 'pedals': 'N/A', 'shifters': 'Shimano Dura-Ace Di2 with sprinter shifters', 'front_derailleur': 'Shimano Dura-Ace Di2', 'rear_derailleur': 'Shimano Dura-Ace Di2', 'brakes': 'Shimano Dura-Ace, hydraulic', 'brake_levers': 'Shimano Di2, hydraulic', 'cassette': 'Shimano Dura-Ace, 11x28', 'chain': 'TK', 'crankset': 'Shimano Dura-Ace with power meter, 36/52', 'bottom_bracket': 'Shimano Press Fit', 'rims': 'Giant SLR-0 Aero Disc WheelSystem (F:42mm, R:65mm)', 'hubs': 'Giant SLR-0 Aero Disc WheelSystem, 12mm thru-axle, CenterLock', 'spokes': 'Giant SLR-0 Aero Disc WheelSystem', 'tires': 'Giant Gavia AC 0 tubeless, 700x25, folding', 'extras': 'RideSense Bluetooth, Race axle', 'weight': 'The most accurate way to determine any bike’s weight is to have your local dealer weigh it for you. Many brands strive to list the lowest possible weight, but in reality weight can vary based on size, finish, hardware and accessories. All Giant bikes are designed for best-in-class weight and ride quality.'}
SAMPLE_SPECS2 = {'sizes': 'S, M, L, XL', 'colors': 'Gun Metal Black / Neon Orange / Charcoal', 'frame': 'Advanced-Grade Composite, ALUXX SL Rear Triangle', 'fork': 'Fox 34 Float Performance Elite, 130mm travel, FIT4 Damper, Boost 15x110mm KaBolt, tapered steerer', 'shock': 'Fox Float DPS Performance Elite, trunnion mount', 'handlebar': 'Giant Contact SL Trail, 780 x 31.8mm', 'stem': 'Giant Contact SL', 'seatpost': 'Giant Contact Switch S dropper post with remote lever, 30.9mm', 'saddle': 'Contact SL (neutral)', 'pedals': 'N/A', 'shifters': 'SRAM NX Eagle, 1x12', 'front_derailleur': 'N/A', 'rear_derailleur': 'SRAM NX Eagle', 'brakes': 'SRAM Guide RS [F] 180mm [R] 160mm, hydraulic disc', 'brake_levers': 'SRAM Guide RS', 'cassette': 'SRAM NX Eagle, 11x50', 'chain': 'SRAM NX Eagle', 'crankset': 'TruVativ Descendent 6k Eagle Dub, Boost, 30', 'bottom_bracket': 'SRAM GXP Dub Press Fit', 'rims': 'Giant TRX 1 Composite DBL WheelSystem, hookless, 30mm inner width, tubeless', 'hubs': 'Giant TRX 1 DBL WheelSystem, pawl driver, Boost, thru-axle, 28h', 'spokes': 'Giant TRX 1 DBL WheelSystem; Dynamic Balanced Lacing, Butted Stainless Steel', 'tires': 'Maxxis high Roller II 27.5x2.3, 60 tpi, EXO, TR, tubeless', 'weight': 'The most accurate way to determine any bike’s weight is to have your local dealer weigh it for you. Many brands strive to list the lowest possible weight, but in reality weight can vary based on size, finish, hardware and accessories. All Giant bikes are designed for best-in-class weight and ride quality.'}
SAMPLE_SPECS3 = {'sizes': 'XS, S, M, L, XL', 'colors': 'Black / Black', 'frame': 'ALUXX SL-grade aluminum', 'fork': 'Advanced-grade composite, OverDrive2 steerer, 12x100QR', 'handlebar': 'Giant Contact, 31.8mm', 'stem': 'Contact', 'seatpost': 'Giant Contact Composite 27,2x375', 'saddle': 'Giant Contact SL, Neutral', 'pedals': 'Platform', 'shifters': 'Shimano Ultegra hydraulic disc', 'front_derailleur': 'Shimano Ultegra', 'rear_derailleur': 'Shimano Ultegra', 'brakes': 'Shimano Ultegra hydraulic disc, 160mm', 'brake_levers': 'Shimano Ultegra hydraulic disc', 'cassette': 'Shimano 105, 11-32, 11-Speed', 'chain': 'KMC e.11 Turbo, EcoProteq, e-bike optimized', 'crankset': 'Giant custom forged by FSA, 34/50', 'rims': 'Giant PR-2 Disc, Tubeless Ready', 'hubs': 'Giant Performance Tracker Road, Sealed Bearing', 'spokes': 'Sapim E-Lite [r] Race [f], e-bike optimized', 'tires': 'Maxxis Re-Fuse 700x32c Folding Carbon Bead MaxxShield Tubeless Ready', 'extras': 'Giant EnergyPak 3A fast charger', 'motor': 'Giant SyncDrive Pro', 'sensors': 'Giant PedalPlus 4-sensor technology', 'display': 'Giant RideControl EVO, grip launch control with walk assist, mini USB charger', 'battery': 'Giant EnergyPak 500, 36V 13.8Ah Rechargeable Lithium-Ion', 'weight': 'The most accurate way to determine any bike’s weight is to have your local dealer weigh it for you. Many brands strive to list the lowest possible weight, but in reality weight can vary based on size, finish, hardware and accessories. All Giant bikes are designed for best-in-class weight and ride quality.'}


class SpecializedTestCase(unittest.TestCase):
    def setUp(self):
        self._fox = FoxValley(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = [
            'road_bikes',
            'mountain_bikes',
            'cross_gravel_bikes',
            'e_bikes',
            'hybrid_city_bikes',
            'kids_bikes',
        ]

        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result = self._fox._get_categories(soup)
        print('categories:', result)
        for key in categories:
            self.assertTrue(key in result,
                            msg=f'{key} is not in result!')

    def test_get_num_bikes(self):
        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')

        num = self._fox._get_max_num_prods(soup)
        expected = 268
        self.assertEqual(expected, num,
                         msg=f'Expected: {expected}; parsed: {num}')

    def test_get_prod_listings(self):
        expected = 30
        with open(SHOP_ROAD_BIKES_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        self._fox._get_prods_on_current_listings_page(
            soup, bike_type='road')
        num_bikes = len(self._fox._products)
        self.assertGreater(num_bikes, expected,
                           msg=f'Expected at least: {expected}; parsed: {num_bikes}')

    def test_get_all_available_prods(self):
        expected = 100
        # Validate method
        self._fox.get_all_available_prods()
        num_prods = len(self._fox._products)
        # There are dupes so expect less num_prods
        self.assertTrue(num_prods > expected,
                        msg=f'expected: {expected} - found: {num_prods}')

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'foxvalley-propel.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text1 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'foxvalley-mtb.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text2 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'foxvalley-eplus.html'))
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
        result = self._fox._parse_prod_specs(detail_soup1)
        self.assertEqual(len(SAMPLE_SPECS1), len(result))
        for key in SAMPLE_SPECS1.keys():
            self.assertEqual(
                SAMPLE_SPECS1[key], result[key])

        # case 2: using second data, exact match in components
        result = self._fox._parse_prod_specs(detail_soup2)
        self.assertEqual(len(SAMPLE_SPECS2), len(result))
        for key in SAMPLE_SPECS2.keys():
            self.assertEqual(SAMPLE_SPECS2[key], result[key])

        # case 3: using third data, exact match in components
        result = self._fox._parse_prod_specs(detail_soup3)
        self.assertEqual(len(SAMPLE_SPECS3), len(result))
        for key in SAMPLE_SPECS3.keys():
            self.assertEqual(SAMPLE_SPECS3[key], result[key],
                             msg=f'{key}: Expected - {SAMPLE_SPECS3[key]}; '
                             f'Result - {result[key]}')


if __name__ == '__main__':
    unittest.main()
