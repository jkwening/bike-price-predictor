# python modules
import unittest
import os
from datetime import datetime

from bs4 import BeautifulSoup

# package modules
from scrapers.canyon import Canyon

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
SHOP_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'canyon.html'))
STRIVE_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'canyon-strive.html'))
ULTIMATE_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'canyon-ultimate.html'))
WMV_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'canyon-wmn-mtb.html'))
SAMPLE_SPECS1 = {'frame': 'Canyon Pathlite AL', 'fork': 'Suntour NRX-D', 'headset': 'Acros AzX 214', 'rear_derailleur': 'Shimano Deore XT Shadow Plus, 11s', 'front_derailleur': 'Shimano SLX, 11s', 'shifters': 'Shimano SLX, 11s', 'brakes': 'Shimano BR MT201 Flatmount', 'hubs': 'Shimano HB-TX505 | Shimano FH-TX505', 'cassette': 'Shimano SLX, 11s', 'rims': 'Alex MD23', 'tires': 'Maxxis Rambler', 'cranks': 'Shimano Deore XT, 11s', 'chainrings': '28 | 38', 'chain': 'Shimano CN-HG601, 11s', 'bottom_bracket': 'Shimano BB-MT800', 'stem': 'Iridium V23', 'handlebar': 'Canyon H40', 'grips': 'Ergon GS 2', 'saddle': 'Iridium Fitness', 'seat_post': 'Iridium S35', 'pedals': 'VP Components  VP-536'}
SAMPLE_SPECS2 = {'frame': 'Canyon Speedmax CF SLX', 'fork': 'Canyon F32 Aero', 'headset': 'Canyon | Acros', 'rear_derailleur': 'Shimano Dura-Ace DI2, 11s', 'derailleur_hanger': 'Derailleur Hanger No. 41', 'front_derailleur': 'Shimano Dura-Ace DI2, 11s', 'shifters': 'Shimano Dura-Ace Di2, 1 Button', 'brake_levers': 'Shimano Dura-Ace Di2, 11s', 'brakes': 'Canyon B11 | B12 integrated Aero', 'cassette': 'Shimano Dura-Ace, 11s', 'wheelset': 'Zipp 858 NSW', 'tires': 'Continental Grand Prix Attack III | Grand Prix Force III', 'cranks': 'Shimano Dura-Ace, 11s', 'chainrings': '53 | 39', 'chain': 'Shimano CN-HG900-11', 'bottom_bracket': 'Shimano Pressfit', 'stem': 'Canyon V19 AL Aero', 'handlebar': 'Canyon HB48 Basebar CF flat', 'extensions': 'Canyon E192 AL Extensions Ergo-S-Bend', 'grips': 'Ergon Canyon Base Bar Grips', 'saddle': 'Fizik Mistica', 'seat_post': 'Canyon S31 CF', 'seat_clamp': 'Canyon integrated', 'nutrition_systems': 'Canyon Energy Box', 'pedals': 'none included'}
SAMPLE_SPECS3 = {'frame': 'Canyon STRIVE CFR', 'rear_shock': 'RockShox Super Deluxe RTR', 'fork': 'RockShox Lyrik RCT3', 'headset': 'Canyon | Acros', 'rear_derailleur': 'SRAM X01 Eagle, 12s', 'chain_guide': 'e.thirteen TRS+', 'shifters': 'SRAM X01 Eagle Trigger, 12s', 'brakes': 'SRAM Code RSC', 'cassette': 'SRAM XG-1295 Eagle, 12s', 'wheelset': 'Mavic Deemax Pro', 'tires': 'Maxxis Minion DHR II 2.4', 'cranks': 'SRAM X01 EAGLE Carbon, 12s', 'chainrings': '32', 'chain': 'SRAM GX Eagle', 'bottom_bracket': 'SRAM DUB BSA', 'stem': 'Canyon G5', 'handlebar': 'Canyon G5 CARBON', 'grips': 'Ergon GD1', 'saddle': 'Ergon SMD20', 'seat_post': 'RockShox Reverb Stealth B1', 'seat_clamp': 'Canyon Race Clamp', 'pedals': 'none included'}


class CanyonTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Canyon(save_data_path=DATA_PATH)

    def test_get_bike_type_models_hrefs(self):
        bike_type = 'mountain'
        model_hrefs = self._scraper._get_bike_type_models_hrefs(bike_type)
        num_models = len(model_hrefs)
        self.assertTrue(num_models > 0,
                        msg=f'{num_models} number of model hrefs.')
        print('\nMTB model hrefs\n', model_hrefs)

    def test_get_prods_listings(self):
        bike_type = 'road'
        model_hrefs = self._scraper._get_bike_type_models_hrefs(bike_type)
        for href in model_hrefs:
            soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
            href), 'lxml')
            self._scraper._get_prods_on_current_listings_page(soup, bike_type)

        # Verify product listings fetch
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 1,
                        msg=f'There are {num_prods} product first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        bike_type = 'road'
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'canyon_prods_all.csv')
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
                    'fork', 'wheel', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')

    def test_get_all_available_prods(self):
        expected = 5  # expect at least one from each bike type
        # Validate method
        self._scraper.get_all_available_prods()
        num_prods = len(self._scraper._products)
        # There are dupes so expect less num_prods
        self.assertTrue(num_prods > expected,
                        msg=f'expected at least: {expected} - found: {num_prods}')


if __name__ == '__main__':
    unittest.main()
