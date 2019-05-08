# python modules
import unittest
import os
from datetime import datetime

from bs4 import BeautifulSoup

# package modules
from scrapers.lynskey import Lynskey

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
SHOP_GRAVEL_HTML_PATH = os.path.abspath(os.path.join(
    HTML_PATH, 'lynskey-gravel-bikes.html'))
SHOP_NEXT_HTML_PATH = os.path.abspath(os.path.join(
    HTML_PATH, 'lynskey-road-next.html'))
SAMPLE_SPECS1 = {'frame_material': 'titanium', 'fork_axle': 'Lynskey Carbon Gravel Fork\xa0with 12mm Thru Axle', 'lever_brakeset': 'Shimano 105 7000 2x11 Speed STI Shifter Set', 'disc_brake_calipers': 'TRP Spyre Flat Mount Mechanical Disc Brake Calipers', 'rear_brake_adaptor': 'TRP Flat to Flat Rear 160mm Adapter', 'front_brake_adaptor': 'TRP Flat to Flat Front 160mm Adapter', 'brake_rotors': 'FSA Afterburner Disc Rotor 160mm (Front and Rear)', 'rear_derailleur': 'Shimano 105 7000 11 speed rear Derailleur medium cage', 'front_derailleur': 'Shimano 105 7000 Double 11 Speed Clamp-on Front Derailleur', 'cassette': 'Shimano 105 7000 Cassette 11-34t', 'crankset': 'FSA Gossamer Pro 386EVO ABS Crankset', 'chain': 'Shimano CN-HG601 QL Chain - 11 spd', 'bottom_bracket': 'MegaEvo BB386 68mm English Threaded Bottom Bracket', 'rear_axle': '12x142 Rear Axle', 'wheelset': 'Vision Team 30 Disc 6-Bolt', 'tire': 'Continental Ultra Sport II Tire 700x28', 'tube': '700c X 28-32mm Presta 48mm tube', 'handlebar': 'FSA Omega Handlebar', 'bar_tape': 'Lynskey Bar Tape - Blk', 'stem': 'FSA Omega stem +/- 6° Rise', 'headset': 'Cane Creek 40 Integrated Headset', 'compression_plug': 'Carbon Steerer\xa0Compression Plug', 'headset_spacer': 'FSA Headset Spacer 5mm - Blk', 'seatpost': 'FSA SL-280 27.2 x 350mm x 20mm Setback Seatpost', 'saddle': 'Lynskey Pro Saddle - Blk'}
SAMPLE_SPECS2 = {'frame_material': 'titanium', 'fork_axle': 'Cane Creek Helm 27.5 - 100mm Fork', 'shifter': 'Shimano SLX M7000 11 Speed Shifter (Standard Clamp Version)', 'brake_levers': 'Magura MT4 Brake Lever with MT4 Disc Caliper', 'brake_rotors': 'Magura Storm SL 160mm Rotor', 'rear_derailleur': 'Shimano SLX RD-M7000 11 Speed Rear Derailleur GS Cage(Shadow)', 'cassette': 'Shimano SLX CS-M7000 11 Speed Cassette 11-46t', 'crankset': 'FSA Afterburner Modular 1x with 32t Chainring', 'bottom_bracket': 'MegaExo 73mm Bottom Bracket', 'chain': 'FSA Team Issue 11speed Chain', 'rear_axle': '12x148 Rear Axle', 'wheelset': 'FSA Afterburner WideR 27.5', 'tire': 'WTB Trail Boss 27.5 x 2.25', 'tube': 'Presta Valve 48mm 27.5 x 2.125-2.35 Tube', 'handlebar': 'FSA Comet Low Rise Handlebars', 'grip': 'WTB Original Trail Grip', 'stem': 'FSA Omega stem +/- 6° Rise', 'headset': 'FSA Orbit C-40-ACB Integrated Headset', 'headset_spacer': 'FSA Headset Spacer 5mm - Black', 'seatpost': 'FSA XC-255 27.2 x 400 Seatpost', 'saddle': 'Lynskey Pro Saddle - Black'}
SAMPLE_SPECS3 = {'frame_material': 'titanium', 'fork_axle': 'Lynskey #5 Carbon Road Fork w/ 12mm Thru Axle', 'lever_brakeset': 'Shimano 105 7000 2x11 Speed STI Shifter Set', 'disc_brake_calipers': 'TRP Spyre Flat Mount Mechanical Disc Brake Calipers', 'rear_brake_adaptor': 'TRP Flat to Flat Rear 160mm Adapter', 'front_brake_adaptor': 'TRP Flat to Flat Front 160mm Adapter', 'brake_rotors': 'FSA Afterburner Disc Rotor 160mm (Front and Rear)', 'rear_derailleur': 'Shimano 105 7000 11 speed rear Derailleur medium cage', 'front_derailleur': 'Shimano 105 7000 Double 11 Speed Clamp-on Front Derailleur', 'cassette': 'Shimano 105 7000 Cassette 11-34t', 'crankset': 'FSA Gossamer Pro 386EVO ABS Crankset', 'chain': 'Shimano CN-HG601 QL Chain - 11 spd', 'bottom_bracket': 'MegaEvo BB386 68mm English Threaded Bottom Bracket', 'rear_axle': '12x142 Rear Axle', 'wheelset': 'Vision Team 30 Disc 6-Bolt', 'tire': 'Continental Ultra Sport II Tire 700x28', 'tube': '700c X 28-32mm Presta 48mm tube', 'handlebar': 'FSA Omega Handlebar', 'bar_tape': 'Lynskey Bar Tape - Blk', 'stem': 'FSA Omega stem +/- 6° Rise', 'headset': 'Cane Creek 40 Integrated Headset', 'compression_plug': 'FSA Compression Plug', 'headset_spacer': 'FSA Headset Spacer 5mm - Blk', 'seatpost': 'FSA SL-280 27.2 x 350mm x 20mm Setback Seatpost', 'saddle': 'Lynskey Pro Saddle - Blk'}


class SpecializedTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Lynskey(save_data_path=DATA_PATH)

    def test_get_prod_listings(self):
        expected = 10
        with open(SHOP_GRAVEL_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        self._scraper._get_prods_on_current_listings_page(
            soup, bike_type='gravel')
        num_bikes = len(self._scraper._products)
        self.assertEqual(num_bikes, expected,
                         msg=f'Expected: {expected}; parsed: {num_bikes}')

    def test_get_next_page(self):
        # Case 1: product page has no next page
        with open(SHOP_GRAVEL_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result, url = self._scraper._get_next_page(soup)
        self.assertFalse(result,
                         msg=f'Expected: False; Result "({result}, {url})"')
        self.assertFalse(url,
                         msg=f'Expected empty string; got {url}')

        # Case 2: product page has next page
        with open(SHOP_NEXT_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result, url = self._scraper._get_next_page(soup)
        self.assertTrue(result,
                        msg=f'Expected: True; Result "({result}, {url})"')
        self.assertTrue(url,
                        msg=f'Expected non-empty string; got {url}')

    def test_get_all_available_prods(self):
        expected = 22
        # Validate method
        self._scraper.get_all_available_prods()
        num_prods = len(self._scraper._products)
        # There are dupes so expect less num_prods
        self.assertTrue(num_prods > expected,
                        msg=f'expected: {expected} - found: {num_prods}')

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'lynskey-cyclocross.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text1 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'lynskey-hardtail.html'))
        with open(html_path, encoding='utf-8') as f:
            prod_detail_text2 = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'lynskey-disc-road.html'))
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
        for key in SAMPLE_SPECS1:
            self.assertEqual(SAMPLE_SPECS1[key], result[key])

        # case 2: using second data, exact match in components
        result = self._scraper._parse_prod_specs(detail_soup2)
        self.assertEqual(len(SAMPLE_SPECS2), len(result))
        for key in SAMPLE_SPECS2:
            self.assertEqual(SAMPLE_SPECS2[key], result[key])

        # case 3: using third data, exact match in components
        result = self._scraper._parse_prod_specs(detail_soup3)
        self.assertEqual(len(SAMPLE_SPECS3), len(result))
        for key in SAMPLE_SPECS3:
            self.assertEqual(SAMPLE_SPECS3[key], result[key])


if __name__ == '__main__':
    unittest.main()
