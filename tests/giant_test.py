# python modules
import unittest
import os
from datetime import datetime

from bs4 import BeautifulSoup

# package modules
from scrapers.giant import Giant

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
SHOP_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'giant-startpage.html'))
SHOP_ROAD_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'giant-aero-race.html'))
SAMPLE_SPECS1 = {'sizes': 'S, M, L', 'colors': 'Space Grey/Green', 'frame': 'ALUXX SL aluminum, Overdrive 1½ - 1⅛" head tube, integrated KS18 kickstand mount', 'fork': 'RST Volante, 60mm travel, tappered steerer, hydraulic lockout', 'handlebar': 'Giant Connect XC Riser', 'stem': 'Giant Connect', 'seatpost': 'Giant 30.9mm, 2-bolt Micro Adjustable, Forged Aluminium', 'saddle': 'Giant Contact Comfort, Upright', 'pedals': 'Aluminum Platform', 'shifters': 'Shimano SL-M2000', 'rear_derailleur': 'Shimano Deore', 'brakes': 'Shimano BR-MT200, hydraulic disc, 180mm', 'brake_levers': 'Shimano BL-MT200', 'cassette': 'Shimano CS-HG201, 11-36T, 9-Speed', 'chain': 'KMC e.9 Sport, e-bike optimized', 'crankset': 'Forged Alloy minimal Q-factor, 42T', 'rims': 'Giant eX 2, Tubeless Ready, 700c aluminium, e-bike optimized', 'hubs': 'Giant eTracker, [F] 100x9mm QR [R] 135mm QR, e-bike optimized', 'spokes': 'Stainless steel', 'tires': 'Giant Crosscut Gravel 2, 700x45c (622x45), Tubeless Ready', 'extras': 'Giant EnergyPak 3A fast charger', 'motor': 'Giant SyncDrive Sport, 80Nm powered by YAMAHA, 350% tuneable support', 'sensors': 'Giant PedalPlus 4-sensor technology', 'display': 'Giant RideControl ONE, remote button', 'battery': 'Giant EnergyPak 400, 36V 11.3Ah Rechargeable Lithium-Ion', 'weight': 'The most accurate way to determine any bike’s weight is to have your local dealer weigh it for you. Many brands strive to list the lowest possible weight, but in reality weight can vary based on size, finish, hardware and accessories. All Giant bikes are designed for best-in-class weight and ride quality.'}
SAMPLE_SPECS2 = {'sizes': 'XS, S, M, M/L, L, XL', 'colors': 'Matte Carbon / Gloss Carbon', 'frame': 'Advanced-Grade Composite, flat mount disc, 12x142mm thru-axle', 'fork': 'Advanced-Grade Composite, full-composite OverDrive steerer, flat mount disc 12mm thru-axle', 'shock': 'N/A', 'handlebar': 'Giant Contact XR D-Fuse, 31.8mm 5-degree back sweep , flare drop', 'stem': 'Giant Connect, 8-degree', 'seatpost': 'Giant D-Fuse, composite', 'saddle': 'Giant Contact SL (neutral)', 'pedals': 'N/A', 'shifters': 'Shimano Ultegra, hydraulic', 'front_derailleur': 'Shimano Ultegra', 'rear_derailleur': 'Shimano Ultegra RX', 'brakes': 'Shimano Ultegra, hydraulic', 'brake_levers': 'Shimano Ultegra', 'cassette': 'Shimano Ultegra, 11x34', 'chain': 'KMC X11SL-1', 'crankset': 'Praxis Zayante, 32/48', 'bottom_bracket': 'Praxis M24 BB86', 'rims': 'Giant CXR-1 Carbon WheelSystem', 'hubs': 'Giant CXR-1 Carbon WheelSystem 12mm thru-axles', 'spokes': 'Giant CXR-1 Carbon WheelSystem', 'tires': 'Giant CrossCut Gravel 1, 700x40, tubeless', 'extras': 'RideSense Compatible', 'weight': 'The most accurate way to determine any bike’s weight is to have your local dealer weigh it for you. Many brands strive to list the lowest possible weight, but in reality weight can vary based on size, finish, hardware and accessories. All Giant bikes are designed for best-in-class weight and ride quality.'}
SAMPLE_SPECS3 = {'sizes': 'S,M,L, XL', 'colors': 'Metallic Wine Burgundy', 'frame': 'ALUXX SL-Grade Aluminum ( OLD 197mm, Tire Max. 27.5”x4.5”) Horizontal Adjustable Dropout System', 'fork': 'Advanced-Grade Composite, alloy OverDrive steerer, 15x150 (fits up to 5.0 tire), Low-rider rack mounts & extra water bottle mounts. Rack & Fender eyelets', 'shock': 'N/A', 'handlebar': 'Giant Connect Trail, 780mm x 31.8mm', 'stem': 'Giant Connect, 8 Degree', 'seatpost': 'Giant Contact Switch, Dropper post (100mm S/125mm M/150mm L&XL) with 1x Remote, 30.9mm', 'saddle': 'Giant Contact (Neutral)', 'pedals': 'N/A', 'shifters': 'SRAM NX Eagle 1x12 Speed', 'front_derailleur': 'N/A', 'rear_derailleur': 'SRAM NX Eagle 12 Speed', 'brakes': 'Level T [F] 180mm [R] 160mm, Hydraulic Disc', 'brake_levers': 'SRAM Level T', 'cassette': 'SRAM PG1230 EAGLE 11-50', 'chain': 'SRAM NX 12 Speed', 'crankset': 'NX EAGLE 12spd FAT5 DUB with 30t Q-Factor 206', 'bottom_bracket': 'SRAM DUB FOR 121mm', 'rims': 'Giant FB27.5, 86mm inner width, Tubeless compatible, AV & PV ready', 'hubs': '▶F: Giant Tracker 15mm x 150mm, Sealed 2 Bearing, 12mm Thru-Axle bolt R : Giant Tracker 12mm x 197mm, Thru-Axle', 'spokes': '14-15-14G STEEL', 'tires': 'Maxxis Colossus 27.5x4.5, TR, EXO, 120 TPI (includes AV inner tubes)', 'extras': 'PV Tubeless Valves', 'weight': 'The most accurate way to determine any bike’s weight is to have your local dealer weigh it for you. Many brands strive to list the lowest possible weight, but in reality weight can vary based on size, finish, hardware and accessories. All Giant bikes are designed for best-in-class weight and ride quality.'}


class SpecializedTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Giant(save_data_path=DATA_PATH)

    def test_get_categories(self):
        expected = 15
        categories = [
            'race_on_road',
            'gravel_on_road',
            'comfort_on_road',
            'comfort_x_road',
            'adventure_x_road',
            'transit_e_bike',
            'bmx_youth',
            'off_road_youth'
        ]

        exclude = [
            'view_all_on_road', 'view_all_x_road',
            'view_all_off_road', 'view_all_e_bike',
            'view_all_youth'
        ]

        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result = self._scraper._get_categories(soup)
        print('categories:', result)
        self.assertGreater(len(result), expected,
                           msg=f'Expected at least {expected}; result = {len(result)}')
        for key in categories:
            self.assertTrue(key in result,
                            msg=f'{key} is not in result!')
        for key in exclude:
            self.assertTrue(key not in result,
                            msg=f'{key} is in result!')

    def test_get_prod_listings(self):
        expected = 4
        with open(SHOP_ROAD_BIKES_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        self._scraper._get_prods_on_current_listings_page(
            soup, bike_type='road')
        num_bikes = len(self._scraper._products)
        self.assertGreater(num_bikes, expected,
                           msg=f'Expected at least: {expected}; parsed: {num_bikes}')

    def test_get_all_available_prods(self):
        expected = 100
        # Validate method
        self._scraper.get_all_available_prods()
        num_prods = len(self._scraper._products)
        # There are dupes so expect less num_prods
        self.assertTrue(num_prods > expected,
                        msg=f'expected: {expected} - found: {num_prods}')

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'giant-explore.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text1 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'giant-revolt.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text2 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'giant-yukon.html'))
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
