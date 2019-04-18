# python modules
import unittest
import os
from datetime import datetime

from bs4 import BeautifulSoup

# package modules
from scrapers.bicycle_warehouse import BicycleWarehouse

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
SHOP_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'bicycle-warehouse.html'))
SAMPLE_SPECS1 = {'frame': 'High-performance hydroformed e-bike frame w/integrated battery and Motor Armor', 'fork': 'Rigid carbon w/15mm thru axle', 'front_hub': 'Bontrager sealed bearing, 15mm alloy axle', 'rear_hub': 'Bontrager sealed cartridge bearing rear hub', 'rims': 'Alex Volar alloy, 27.5˝, 32h', 'tires': 'Schwalbe Super Moto-X w/GreenGuard puncture protection, 650Bx2.40', 'shifters': 'Shimano Deore M6000, 10 speed', 'rear_derailleur': 'Shimano Deore M6000, shadow Plus', 'crank': 'Miranda Delta, 18T w/chainguard', 'cassette': 'Shimano HG500, 11-42, 10-speed', 'chain': 'KMC X10E', 'pedals': 'Wellgo track-style alloy', 'saddle': 'Bontrager H1', 'seatpost': 'Bontrager alloy, 2-bolt head, 31.6mm, 8mm offset', 'handlebar': 'Bontrager alloy, 31.8mm, 15mm rise', 'grips': 'Bontrager Satellite Elite, lock-on, ergonomic', 'stem': 'Bontrager Elite Blendr, w/mount for Supernova light', 'headset': 'Integrated, cartridge bearing, sealed, 1-1/8˝ top, 1.5˝ bottom', 'brakeset': 'Shimano M315, hydraulic disc', 'battery': 'Bosch PowerPack 500Wh, integrated in frame', 'controller': 'Bosch Purion', 'motor': 'Bosch Performance Line, 250 watt, 63Nm, 20 mph', 'front_light': 'Supernova Mini 2, 205 lumen w/daytime running light', 'rear_light': 'Supernova E3 rear light, LED', 'extras': '2A Bosch Charger', 'weight_limit': 'This bike has a maximum total weight limit (combined weight of bicycle, rider, and cargo) of 300 pounds (136 kg).'}
SAMPLE_SPECS2 = {'frame': '600 Series OCLV Carbon, Front IsoSpeed, Adjustable Rear IsoSpeed, tapered head tube, BB90, flat mount disc brakes, 12mm thru-axle, internal cable routing, hidden fender mounts, 3S chain keeper, DuoTrap S compatible, Ride Tuned seatmast', 'fork': 'Domane full carbon disc, carbon tapered steerer, flat mount disc brakes, 12mm thru-axle', 'wheels': 'Bontrager Paradigm Comp Tubeless Ready Disc, 12mm thru axle', 'tires': 'Bontrager R3 Hard-Case Lite, 120 tpi, aramid bead, 700x32c', 'max_tire_size': '32c Bontrager tires (with at least 4mm of clearance to frame)', 'shifters': 'Shimano Ultegra, 11 speed', 'front_derailleur': 'Shimano Ultegra, braze-on', 'rear_derailleur': 'Shimano Ultegra, 11 speed', 'crank': 'Shimano Ultegra, 50/34 (compact)', 'bottom_bracket': 'BB90', 'cassette': 'Shimano Ultegra, 11-32, 11 speed', 'chain': 'Shimano Ultegra', 'pedals': 'Not included', 'saddle': 'Bontrager Arvada Elite, stainless rails', 'seatpost': 'Bontrager Ride Tuned carbon seatmast cap, 20mm offset', 'handlebar': 'Bontrager Pro IsoCore VR-CF, 31.8mm', 'grips': 'Bontrager tape', 'stem': 'Bontrager Pro, 31.8mm, 7 degree, w/computer & light mounts', 'headset': 'Integrated, cartridge bearing, sealed, 1-1/8˝ top, 1.5˝ bottom', 'brakeset': 'Shimano Ultegra flat mount hydraulic disc', 'weight': '56cm - 8.11 kg / 17.88 lbs', 'weight_limit': 'This bike has a maximum total weight limit (combined weight of bicycle, rider, and cargo) of 275 pounds (125 kg).'}
SAMPLE_SPECS3 = {'frame': 'Alpha Platinum Aluminum, ABP, Boost148, Knock Block steerer stop, Full Floater, EVO link, tapered head tube, Mino Link, Control Freak internal routing, down tube guard, PF92, ISCG 05, G2 Geometry, 130mm travel', 'front_suspension': 'Fox Rhythm 34 Float, GRIP adjustable damper, tapered steerer, G2 Geometry w/51mm offset, Boost110, 130mm travel', 'rear_suspension': 'Fox Performance Float EVOL, RE:aktiv 3-position damper, tuned by Trek Suspension Lab, 210x52.5mm', 'wheels': 'Bontrager Line Comp 30, Tubeless Ready, 54T Rapid Drive, Boost110 front, Boost148 rear, tubeless strips included, valves sold separately', 'tires': 'Bontrager XR4 Team Issue, Tubeless Ready, Inner Strength sidewalls, 120tpi, aramid bead, 29x2.40˝', 'shifters': 'SRAM GX Eagle, 12 speed', 'rear_derailleur': 'SRAM GX Eagle, Roller Bearing Clutch', 'crank': 'Truvativ Descendant 6k Eagle DUB, 32T Direct Mount', 'bottom_bracket': 'SRAM DUB Press Fit, 92mm', 'cassette': 'SRAM XG-1275 Eagle, 10-50, 12 speed', 'chain': 'SRAM GX Eagle', 'pedals': 'Not included', 'saddle': 'Bontrager Arvada, hollow chromoly rails', 'seatpost': 'Bontrager Line, internal routing, 31.6mm, 15.5: 100mm, 17.5 & 18.5: 125mm, 19.5 & 21.5: 150mm', 'handlebar': 'Bontrager Line, 35mm, 15mm rise, 750mm width', 'grips': 'Bontrager XR Trail Elite, alloy lock-on', 'stem': 'Bontrager Line, Knock Block, 35mm clamp, 0 degree', 'headset': 'Knock Block Integrated, sealed cartridge bearing, 1-1/8˝ top, 1.5˝ bottom', 'brakeset': 'Shimano Deore M6000 hydraulic disc', 'weight': '17.5˝ - 13.79 kg / 30.4 lbs (with tubes)', 'weight_limit': 'This bike has a maximum total weight limit (combined weight of bicycle, rider, and cargo) of 300 pounds (136 kg).'}


class SpecializedTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = BicycleWarehouse(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = [
            'road_bikes',
            'mountain_bikes',
            'electric_bikes',
            'kids_bikes',
            'path_pavement_bikes',
            'bmx'
        ]

        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result = self._scraper._get_categories(soup)
        print('categories:', result)
        self.assertEqual(len(categories), len(result),
                         msg=f'Expected {len(categories)}; result {len(result)}')
        for key in categories:
            self.assertTrue(key in result,
                            msg=f'{key} is not in result!')

    def test_get_num_bikes(self):
        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')

        num = self._scraper._get_max_num_prods(soup)
        expected = 268
        self.assertEqual(expected, num,
                         msg=f'Expected: {expected}; parsed: {num}')

    def test_get_prod_listings(self):
        expected = 23
        with open(SHOP_BIKES_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        self._scraper._get_prods_on_current_listings_page(
            soup, bike_type='all')
        num_bikes = len(self._scraper._products)
        self.assertEqual(num_bikes, expected,
                         msg=f'Expected: {expected}; parsed: {num_bikes}')

    def test_get_all_available_prods(self):
        # Validate method
        self._scraper.get_all_available_prods()
        num_prods = len(self._scraper._products)
        # There are dupes so expect less num_prods
        self.assertTrue(num_prods > 150,
                        msg=f'expected: {150} - found: {num_prods}')

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'trek-Commuter.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text1 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'trek-Domane.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text2 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'trek-Fuel-EX.html'))
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
