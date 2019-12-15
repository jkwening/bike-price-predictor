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
SHOP_BIKES_HTML_PATH = os.path.abspath(os.path.join(HTML_PATH, '_scraper.html'))
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
        self._scraper = Rei(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = ['mountain', 'road', 'kids',
                      'specialty', 'hybrid', 'electric']

        result = self._scraper._get_categories()
        print('\nCategories:', result)
        self.assertEqual(len(categories), len(result),
                         msg=f'Expected {len(categories)}; result {len(result)}')
        for key in result.keys():
            self.assertTrue(key in categories,
                            msg=f'{key} is not in {categories}!')

    def test_get_prods_listings(self):
        bike_type = 'road'
        categories = self._scraper._get_categories()
        bike = categories[bike_type]['href'].split('/')[-1]
        data = json.loads(
            self._scraper._fetch_prod_listing_view(
                page_size=self._scraper._page_size, bike=bike
            )
        )

        # Verify product listings fetch
        self._scraper._get_prods_on_current_listings_page(data, bike_type)
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 5,
                        msg=f'There are {num_prods} product first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        bike_type = 'road'
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'rei_prods_all.csv')
        # Verify parsing product specs
        specs = self._scraper.get_product_specs(get_prods_from=prods_csv_path,
                                                bike_type=bike_type,
                                                to_csv=False)
        num_prods = len(self._scraper._products)
        num_specs = len(specs)
        self.assertEqual(num_prods, num_specs,
                         msg=f'Products size: {num_prods}, Specs size: {num_specs}')
        self._scraper._write_prod_specs_to_csv(specs=specs,
                                               bike_type=bike_type)

        # Verify spec fieldnames has minimum general fields:
        expected = ['site', 'product_id', 'frame',
                    'fork', 'number_of_gears', 'saddle', 'seat_post']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
