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
SHOP_BIKES_HTML_PATH = os.path.abspath(os.path.join(HTML_PATH,
                                                    'bicycle-warehouse.html'))
SHOP_ROAD_HTML_PATH = os.path.abspath(os.path.join(
    HTML_PATH, 'bicycle-warehouse-roadbikes.html'))
SHOP_ROAD_FROM_HTML_PATH = os.path.abspath(os.path.join(
    HTML_PATH, 'bicycle-warehouse-roadbikes-from.html'))
SHOP_NO_NEXT_HTML_PATH = os.path.abspath(os.path.join(
    HTML_PATH, 'bicycle-warehouse-no-next.html'))
SAMPLE_SPECS1 = {'frame': 'Reynolds 631 Chromoly Custom Butted, Tapered Headtube, 142x12mm Thru Axles, Disc Tabs', 'fork': 'Carbon/Alloy Tapered Steer, Post Mount Disc, 15mm Thru Axles', 'headset': 'Integrated Cartridge Bearings', 'cranks': 'Praxis Works Alba M30, 38 Tooth Direct Mount', 'bottom_bracket': 'Praxis Works M30 External Bearings', 'rear_derailleur': 'SRAM Rival 1, 11 Speed', 'shifter': 'SRAM Rival 1 HRD, 11 Speed', 'cogset_cassette_freewheel': 'SRAM PG1130, 11 Speed, 11-42', 'chain': 'KMC X11EL-1', 'front_hub': 'Alloy Disc, Cartridge Bearing, 15mm Thru Axle, 28 Hole', 'rear_hub': 'Alloy Disc, Cartridge Bearing, Thru Axle, 28 Hole', 'spokes': '14/15g Butted Stainless with Brass Nipples', 'rims': 'HED Tomcat Disc, 28 Hole, Tubless Compatible', 'tires': "Clement X'PLOR MSO, 700x40c, 60TPI, Folding", 'brakes': 'SRAM Rival Hydraulic Disc, 160mm Rotors', 'brake_levers': 'SRAM Rival', 'pedals': 'Resin Platform Pedal', 'handlebar': 'HED Eroica, 31.8 with 16 Degree Flare, 38/40/42/44/46', 'stem': 'HED Eroica, 31.8, Lengths:/90/100/110/mm', 'seat': 'WTB Volt Race', 'seatpost': 'HED Eroica, 27.2', 'extras': 'Tubeless Valves, Rack and Fender Mounts, third bottle cage mount, Travel Bag'}
SAMPLE_SPECS2 = {'sizes': 'XS, S, M, M/L, L, XL', 'colors': 'Neon Red / Black Chrome, Matte Black / Gloss Black', 'frame': 'ALUXX SL-Grade Aluminum', 'fork': 'Advanced-Grade Composite, alloy OverDrive steerer', 'shock': 'N/A', 'handlebar': 'Giant Connect flat', 'stem': 'Giant Connect, 8-degree', 'seatpost': 'Giant D-Fuse, composite', 'saddle': 'Giant Contact (neutral)', 'pedals': 'Platform', 'shifters': 'Shimano Tiagra, 2x10', 'front_derailleur': 'Shimano Tiagra', 'rear_derailleur': 'Shimano Tiagra', 'brakes': 'TRP flat mount HD-R210 {F] 140mm rotor [R] 140mm rotor, custom caliper', 'brake_levers': 'TRP HD-R210', 'cassette': 'CS-HG500, 11x34', 'chain': 'KMC X10 with Missing Link', 'crankset': 'FC-RS400, 34/50', 'bottom_bracket': 'Shimano, threaded', 'rims': 'Giant S-R2 disc, tubeless wheelset', 'hubs': 'Giant S-R2 disc, tubeless wheelset', 'spokes': 'Giant S-R2 disc, tubeless wheelset', 'tires': 'Gavia AC 2 tubeless, 700x28', 'extras': 'Contact Ergo Max bar end'}
SAMPLE_SPECS3 = {'sizes': 'XS, S, M, L, XL', 'colors': 'Metallic Black / Metallic Orange, Glacier Green/ Pure Red / Navy Blue', 'frame': 'ALUXX SL-Grade Aluminum', 'fork': 'Suntour AION 35-Boost RC DS 27.5+, 150mm travel, Boost QR15x110mm, tapered steerer', 'shock': 'RockShox Deluxe R, trunnion mount', 'handlebar': 'Giant Connect Trail, 780x31.8mm', 'stem': 'Giant Connect', 'seatpost': 'Giant Contact Switch dropper post with remote lever, 30.9mm', 'saddle': 'Giant Contact (neutral)', 'pedals': 'N/A', 'shifters': 'Shimano Deore, 1x10', 'front_derailleur': 'N/A', 'rear_derailleur': 'Shimano Deore , Shadow+', 'brakes': 'Shimano BR-MT400 [F] 180mm [R] 180mm, hydraulic disc', 'brake_levers': 'Shimano BL-MT400', 'cassette': 'Shimano Deore CS-HG500-10, 11x42', 'chain': 'KMC X10-1', 'crankset': 'Praxis Cadet, Boost, 30', 'bottom_bracket': 'Praxis BB-90 Press Fit', 'rims': 'Giant AM 27.5, tubeless ready, sleeve-joint rim, 30mm inner width', 'hubs': '[F] Giant Tracker Performance Boost 15x110mm, sealed bearing [R] Giant Tracker Performance, Boost 12x148, sealed bearing', 'spokes': 'Sapim', 'tires': '[F] Maxxis high Roller II 27.5x2.5 WT, 60 tpi, EXO, TR [R] Maxxis high Roller II 27.5x2.4, 60 tpi, EXO, TR, tubeless'}
SAMPLE_SPECS4 = {'available_frame_sizes': 'S, M, L', 'available_colors': 'SANTA FE SAND; MILLITARY GREEN / CEMENT GREY', 'frame': 'NINER RDO CARBON FIBER, 140MM TRAVEL, GEO FLIP CHIP, RIB CAGE CONSTRUCTION, FULL SLEEVE CABLE ROUTING, ENDURO MAX BLACK OXIDE PIVOT BEARINGS', 'fork': 'FOX 36 FLOAT RHYTHM GRIP EVOL, SWEEP ADJUST, 150MM, 110X15MM, 44MM OFFSET', 'shock': 'FOX FLOAT DPX2 PERFORMANCE EVOL 3 POSITION', 'tubes_sealant': 'STANS NO TUBES SEALANT (2 X 2OZ BOTTLES)', 'front_wheel': 'NINER ALLOY, 110X15MM FRONT, NINER GRAPHIC', 'rear_wheel': 'NINER ALLOY, 148X12MM REAR, NINER GRAPHIC', 'front_tire': 'MAXXIS MINION DHF 3C/EXO/TR 2.5 WT FRONT', 'rear_tire': 'MAXXIS AGGRESSOR 2C/EXO/TR 2.5 WT REAR', 'brakes': 'SRAM LEVEL', 'brake_levers': 'SRAM LEVEL', 'brake_rotors': '180/180MM G2CS ROTORS', 'chain': 'SRAM NX EAGLE 12SP', 'front_shifter': 'N/A', 'rear_shifter': 'SRAM NX EAGLE 12SP', 'front_derailleur': 'N/A', 'rear_derailleur': 'SRAM PG 1230 11-50T', 'cassette': 'SRAM NX EAGLE 12SP', 'crankset': 'SRAM NX EAGLE DUB 32T', 'bottom_bracket': 'SRAM DUB BSA THREADED', 'saddle': 'NINER CUSTOM TR WITH CR-MO RAILS, PRINTED NINER GRAPHIC', 'seatpost': 'SDG TELLIS (S-125MM, M-150MM, L/XL-170MM)', 'handlebar': 'RACE FACE AEFFECT R 780MM WIDE, 20MM RISE, 35MM CLAMP', 'stem': 'RACE FACE AEFFECT R 40MM, 35MM CLAMP', 'headset': 'NINER INTERNAL ZS SHIS DESCRIPTION ZS44/28.6|ZS56/40', 'grips': 'NINER GRRRIPS L/O NYLON FLANGED'}


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
        with open(SHOP_ROAD_HTML_PATH, mode='r', encoding='utf-8') as html:
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
        expected = 24
        with open(SHOP_ROAD_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        self._scraper._get_prods_on_current_listings_page(
            soup, bike_type='road')
        num_bikes = len(self._scraper._products)
        self.assertEqual(num_bikes, expected,
                         msg=f'Expected: {expected}; parsed: {num_bikes}')

        # Caser "from" text
        expected *= 2
        with open(SHOP_ROAD_FROM_HTML_PATH, mode='r',
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
            HTML_PATH, 'bicycle-warehouse-COBI.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text1 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'bicycle-warehouse-FastRoad.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text2 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'bicycle-warehouse-Trance.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text3 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'bicycle-warehouse-4cols.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text4 = f.read()

        detail_soup1 = BeautifulSoup(
            prod_detail_text1, 'lxml')
        detail_soup2 = BeautifulSoup(
            prod_detail_text2, 'lxml')
        detail_soup3 = BeautifulSoup(
            prod_detail_text3, 'lxml'
        )
        detail_soup4 = BeautifulSoup(
            prod_detail_text4, 'lxml'
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

        # case 4: 4 columns in specs table
        result = self._scraper._parse_prod_specs(detail_soup4)
        self.assertEqual(len(SAMPLE_SPECS4), len(result))
        for key in SAMPLE_SPECS4.keys():
            self.assertEqual(SAMPLE_SPECS4[key], result[key])


if __name__ == '__main__':
    unittest.main()
