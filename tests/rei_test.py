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
SYNAPSE_SPECS = {
    'best_use': 'Cycling',
    'frame': 'Synapse Disc asymmetric, BallisTec carbon, Di2 ready, SAVE, BB30a, 12mm thru axle',
    'fork': 'Synapse Disc asymmetric, SAVE PLUS, BallisTec carbon',
    'bike_suspension': 'No Suspension',
    'crankset': 'SRAM Apex 1 BB30a 44T X-Sync',
    'bottom_bracket': 'FSA BB30A',
    'shifters': 'SRAM Apex 1 HRD',
    'rear_derailleur': 'SRAM Apex 1 Long cage',
    'rear_cogs': 'SRAM PG 1130, 11-42, 11-speed',
    'number_of_gears': '11 gear(s)',
    'brake_type': 'Hydraulic Disc Brake',
    'brakes': 'SRAM Apex 1 hydro disc, flat mount, 160/160mm',
    'rims': 'WTB STP i19 TCS 28-hole, tubeless ready',
    'front_hub': 'Formula RX-512',
    'rear_hub': 'RX-142',
    'wheel_size': '700c',
    'tires': 'WTB Exposure, 700Cx30mm, tubeless ready, gumwall',
    'tire_width': '30 millimeters',
    'handlebar_shape': 'Drop Bar',
    'handlebar': 'Cannondale C3, butted 6061 alloy, compact',
    'stem': 'Cannondale C3, 6061 alloy, 31.8mm, 6 deg.',
    'seat_post': 'Cannondale C3; 6061 alloy; 25.4x350mm (48-56), 400mm (58-61)',
    'saddle': 'Fabric Scoop Radius Sport',
    'pedals': 'Sold separately',
    'headset': 'Synapse Si, 1-1/4 in. lower bearing, 25mm top cap',
    'chain': 'SRAM PC 1110, 11-speed',
    'weight': '20 pounds',
    'bike_weight': 'Bike weight is based on median size, as sold, or the average of two median sizes.',
    'gender': 'Unisex'
}


class ReiTestCase(unittest.TestCase):
    def setUp(self):
        self.rei = Rei(save_data_path=DATA_PATH)

    def test_get_categories(self):
        expected = {
            'mountain': {'href': '/c/mountain-bikes', 'total': 81},
            'road': {'href': '/c/road-bikes', 'total': 52},
            "kids'": {'href': '/c/kids-bikes', 'total': 51},
            'specialty': {'href': '/c/specialty-bikes', 'total': 38},
            'hybrid': {'href': '/c/hybrid-bikes', 'total': 29},
            'electric': {'href': '/c/electric-bikes', 'total': 27}
        }

        # load test bikes rei page
        html_path = os.path.abspath(os.path.join(HTML_PATH,
                                                 'rei.html'))
        with open(html_path, encoding='utf-8') as f:
            html = f.read()

        categories = self.rei.get_categories(soup=BeautifulSoup(html, 'lxml'))
        for key in expected:
            self.assertTrue(key in categories,
                            msg=f'{key} not in {categories}')
            self.assertDictEqual(expected[key], categories[key],
                                 msg=f'Dictionary does not match for {key}')

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
            'REI-Outlet-Synapse.html'))
        with open(html_path, encoding='utf-8') as f:
            synapse_prod_detail_text = f.read()

        stromer_detail_soup = BeautifulSoup(stromer_prod_detail_text, 'lxml')
        synapse_detail_soup = BeautifulSoup(synapse_prod_detail_text,
                                                  'lxml')

        # case 1: exact match per example data
        result = self.rei._parse_prod_specs(stromer_detail_soup)
        self.assertEqual(len(STROMER_SPECS), len(result))
        for key in STROMER_SPECS.keys():
            self.assertEqual(STROMER_SPECS[key], result[key])

        # case 2: using second data, exact match in components
        result = self.rei._parse_prod_specs(synapse_detail_soup, garage=True)
        self.assertEqual(len(SYNAPSE_SPECS), len(result))
        for key in SYNAPSE_SPECS.keys():
            self.assertEqual(SYNAPSE_SPECS[key], result[key])


if __name__ == '__main__':
    unittest.main()
