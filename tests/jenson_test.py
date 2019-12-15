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
        categories = ['mountain_bikes', 'road_bikes', 'cyclocross_gravel_bikes',
                      'electric_bikes', 'commuter_urban_bikes', 'bmx_bikes',
                      'kids_bikes', 'corona_store_exclusives']

        result = self._scraper._get_categories()
        print('\nCategories:', result)
        self.assertEqual(len(categories), len(result),
                         msg=f'Expected {len(categories)}; result {len(result)}')
        for key in categories:
            self.assertTrue(key in result,
                            msg=f'{key} is not in {result}!')

    def test_get_prods_listings(self):
        bike_type = 'road_bikes'
        bike_cats = self._scraper._get_categories()
        endpoint = bike_cats[bike_type]['href']
        soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
            endpoint), 'lxml')

        # Verify product listings fetch
        self._scraper._get_prods_on_current_listings_page(soup, bike_type)
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 5,
                        msg=f'There are {num_prods} product first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        bike_type = 'road_bikes'
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'jenson_prods_all.csv')
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
                    'fork', 'cassette', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')

    def test_get_all_available_prods(self):
        self._scraper.get_all_available_prods()
        expected = 400
        num_prods = len(self._scraper._products)
        # There are dupes so expect less num_prods
        self.assertTrue(expected >= num_prods,
                        msg=f'Expected: {expected} - found: {num_prods}')


if __name__ == '__main__':
    unittest.main()
