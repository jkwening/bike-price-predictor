# python modules
import unittest
import os
from datetime import datetime
import json

from bs4 import BeautifulSoup

# package modules
from scrapers.rei import Rei

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
TEST_PROD_LISTING_PATH = os.path.join(TEST_DATA_PATH, 'performance_prod_listing_test_data.csv')
SHOP_BIKES_HTML_PATH = os.path.abspath(os.path.join(HTML_PATH, 'rei.html'))
STROMER_SPECS = {
    'best_use': 'Bike Commuting',
    'motor': 'SYNO Drive 500W 40Nm',
    'battery_type': 'Lithium Ion',
    'charge_time_hrs': '4 - 8 hours',
    'pedal_assist_range': '90 miles',
    'frame': 'Stromer Alloy',
    'bike_suspension': 'No Suspension',
    'fork': 'Stromer Carbon',
    'crankset': 'FSA Gossamer 52-36T',
    'bottom_bracket': 'FSA',
    'shifters': 'Shimano SLX',
    'front_derailleur': 'NIL',
    'rear_derailleur': 'Shimano Deore XT',
    'rear_cogs': 'Shimano SLX, 11-34, 20-speed',
    'number_of_gears': '20 gear(s)',
    'brake_type': 'Hydraulic Disc Brake',
    'brakes': 'Magura MT Next E-MT4',
    'brake_levers': 'Magura MT Next E-MT4',
    'rims': 'DT-Swiss 545D',
    'front_hub': 'Formula DC71',
    'rear_hub': 'Syno Drive 500W Hub Motor',
    'wheel_size': '26 inches',
    'tires': 'Schwalbe Big Ben, 26 x 2.15',
    'tire_width': '2.15 inches',
    'handlebar_shape': 'Flat Bar',
    'handlebar': 'Stromer Custom Alloy',
    'stem': 'Stromer Custom Alloy',
    'seat_post': 'Stromer JD-SP100 Alloy',
    'saddle': 'Stromer Custom',
    'pedals': 'Stromer Custom Alloy',
    'headset': 'Stromer Custom Sealed Cartidge',
    'chain': 'Shimano CN-HG54',
    'weight': '65 pounds',
    'bike_weight': 'Bike weight is based on median size, as sold, or the average of two median sizes.',
    'gender': 'Unisex',
    'battery_removable': 'Yes',
    'motor_torque_nm': '35',
    'motor_type': 'Direct-Drive Hub',
    'e_bike_classification': 'Class 3: high-speed pedal assist'}
DRT_SPECS = {
    'best_use': 'Mountain Biking',
    'mountain_bike_style': 'Trail',
    'frame': 'Co-op Cycles 6061 double-butted aluminum',
    'bike_suspension': 'Front Suspension',
    'fork': 'SR Suntour 27.5 air sprung suspension fork with rebound adjustment and remote lockout',
    'fork_travel': '120 millimeters',
    'crankset': 'Shimano FC-M6000-2, Deore, 36/22',
    'bottom_bracket': 'Shimano',
    'shifters': 'Shimano SL-M6000-IL Deore, Rapidfire Plus',
    'front_derailleur': 'Shimano FD-M6025-D Deore',
    'rear_derailleur': 'Shimano SLX Shadow Plus',
    'rear_cogs': 'Shimano CS-HG500-10, 11-42T, 10 speed',
    'number_of_gears': '20',
    'brake_type': 'Hydraulic Disc Brake',
    'brakes': 'Shimano BL/BR-MT500 hydraulic disc brake, Shimano Deore centerlock rotor 180mm/160mm',
    'brake_levers': 'Shimano M425',
    'rims': 'Weinmann U28, alloy 32h, double wall, single eyelet',
    'front_hub': 'Joytech D041 loose ball disc hub; 15mm thru-axle; 32h',
    'rear_hub': 'Shimano, center lock rotor; 32h',
    'wheel_size': '27.5 inches',
    'tires': 'Schwalbe Tough Tom 27.5 x 2.35 front, 27.5 x 2.25 rear',
    'tire_width': '2.35 inches',
    'handlebar_shape': 'Riser Bar',
    'handlebar': 'Co-op Cycles AL6061 double-butted, 11mm rise; 7 deg backsweep; 5 deg upsweep; 740 width',
    'stem': 'Co-op Cycles 6061 aluminum, 31.8, 0 degree rise',
    'seat_post': 'Co-op Cycles 6016 AL, 31.6 diameter, 5mm offset',
    'saddle': 'WTB Volt Sport',
    'pedals': 'Co-op Cycles MTB style with alloy cage',
    'headset': 'Co-op Cycles internal cartridge bearing with alloy upper and lower cups',
    'chain': 'Shimano CN-HG54, 10 speed',
    'weight': '29 lbs. 2.7 oz.',
    'bike_weight': 'Bike weight is based on median size, as sold, or the average of two median sizes.',
    'gender': 'Unisex'}

class ReiTestCase(unittest.TestCase):
    def setUp(self):
        self.rei = Rei(save_data_path=DATA_PATH)

    def test_fetch_prod_listing_view(self):
        # required data fields expected in JSON repsonse
        req_data_keys = [
            'searchStatus', 'results', 'query'
        ]
        req_query_keys = [
            'totalResults', 'upperResult'
        ]
        req_results_keys = [
            'cleanTitle', 'brand', 'prodId', 'link', 'displayPrice'
        ]
        req_display_price_keys = [
            'max', 'compareAt'
        ]

        # convert to response to JSON and validate required fields
        data = json.loads(self.rei._fetch_prod_listing_view())
        for expected in req_data_keys:
            self.assertTrue(expected in data.keys(),
                msg=f'{expected} not in response keys: {data.keys()}')
        for expected in req_query_keys:
            query = data['query']
            self.assertTrue(expected in query.keys(),
                msg=f'{expected} not in query keys: {query.keys()}')
        for expected in req_results_keys:
            result = data['results'][0]
            self.assertTrue(expected in result.keys(),
                msg=f'{expected} not in result keys: {result.keys()}')
        for expected in req_display_price_keys:
            display_price = data['results'][0]['displayPrice']
            self.assertTrue(expected in display_price.keys(),
                msg=f'{expected} not in display price keys: {display_price.keys()}')
    
    def test_get_prod_listings(self):
        data = json.loads(self.rei._fetch_prod_listing_view(page_size=self.rei._page_size))
        num_prods = int(data['query']['totalResults'])
        self.rei.get_all_available_prods(to_csv=True)
        self.assertEqual(num_prods, self.rei._num_bikes,
            msg=f'Number of bikes = {num_prods}, parsed: {self.rei._num_bikes}')

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(HTML_PATH,
            'rei-STROMER-Electric-Bike.html'))
        with open(html_path, encoding='utf-8') as f:            
            stromer_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(HTML_PATH,
            'rei-Co-op-DRT.html'))
        with open(html_path, encoding='utf-8') as f:
            drt_prod_detail_text = f.read()

        # html_path = os.path.abspath(os.path.join(HTML_PATH,
        #     'rei-Vitus-Vitesse-Road-Bike.html'))
        # with open(html_path, encoding='utf-8') as f:
        #     vitus_prod_detail_text = f.read()

        # html_path = os.path.abspath(os.path.join(HTML_PATH, 'bike-eli-elliptigo-sub-31-8914.html'))
        # with open(html_path, encoding='utf-8') as f:
        #     generic_error = f.read()

        stromer_detail_soup = BeautifulSoup(stromer_prod_detail_text, 'lxml')
        drt_detail_soup = BeautifulSoup(drt_prod_detail_text,
                                                  'lxml')
        # vitus_detail_soup = BeautifulSoup(vitus_prod_detail_text, 'lxml')
        # generic_error_soup = BeautifulSoup(generic_error, 'lxml')

        # case 1: exact match per example data
        result = self.rei._parse_prod_specs(stromer_detail_soup)
        self.assertEqual(len(STROMER_SPECS), len(result))
        for key in STROMER_SPECS.keys():
            self.assertEqual(STROMER_SPECS[key], result[key])

        # case 2: using second data, exact match in components
        result = self.rei._parse_prod_specs(drt_detail_soup)
        self.assertEqual(len(DRT_SPECS), len(result))
        for key in DRT_SPECS.keys():
            self.assertEqual(DRT_SPECS[key], result[key])

        # # case 3: using third data, exact match in components
        # result = self.rei._parse_prod_specs(vitus_detail_soup)
        # self.assertEqual(len(VITUS_SPECS), len(result))
        # for key in VITUS_SPECS.keys():
        #     self.assertEqual(VITUS_SPECS[key], result[key])

        # # case 4: safely handle error TODO
        # result = self.rei._parse_prod_specs(generic_error_soup)
        # self.assertEqual(0, len(result))


if __name__ == '__main__':
    unittest.main()
