# python modules
import unittest
import os
from datetime import datetime

from bs4 import BeautifulSoup

# package modules
from scrapers.backcountry import BackCountry

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
SHOP_BIKES_HTML_PATH = os.path.abspath(os.path.join(HTML_PATH,
                                                    'backcountry.html'))
SHOP_SALE_HTML_PATH = os.path.abspath(os.path.join(
    HTML_PATH, 'backcountry-sale.html'))
SHOP_NO_NEXT_HTML_PATH = os.path.abspath(os.path.join(
    HTML_PATH, 'backcountry-tt.html'))
SAMPLE_SPECS1 = {'frame_material': 'carbon CC', 'suspension': 'VPP', 'rear_shock': 'FOX Float Performance Elite DPX', 'rear_travel': '150mm', 'fork': 'FOX 36 Float Factory', 'front_travel': '150mm', 'headset': 'Cane Creek 40 IS Integrated', 'shifters': 'SRAM X01 Eagle (12-speed)', 'rear_derailleur': 'SRAM X01 Eagle (12-speed)', 'iscg_tabs': 'ISCG-05', 'crankset': 'SRAM X1 Eagle DUB', 'chainring_sizes': '30t', 'crank_arm_length': '[x-small - small] 170mm, [medium - x-large] 175mm', 'bottom_bracket': 'SRAM DUB', 'bottom_bracket_type': 'BSA threaded', 'cassette': 'SRAM XG1295 Eagle (12-speed)', 'cassette_range': '10 - 50t', 'chain': 'SRAM X01 Eagle (12-speed)', 'brakeset': 'SRAM Code RSC', 'brake_type': 'hydraulic disc', 'rotors': '[front] 200mm Avid Centerline, [rear] 180mm Avid Centerline', 'handlebar': 'SCB AM Carbon', 'grips': 'Santa Cruz Palmdale', 'stem': 'Race Face Aeffect R', 'stem_length': '50mm', 'saddle': 'WTB Silverado Team', 'seatpost': 'RockShox Reverb Stealth', 'wheelset': 'Santa Cruz Reserve 30 Carbon', 'hubs': 'DT Swiss 350', 'front_axle': '15mm Boost', 'rear_axle': '12 x 148mm', 'tires': '[front] Maxxis Minion DHR II 3C Silkshield, [rear] Maxxis Minion DHR II 3C Silkshield', 'tire_size': '29 x 2.4in', 'pedals': 'not included', 'claimed_weight': '28lb 11oz', 'recommended_use': 'enduro, trail', 'manufacturer_warranty': 'lifetime on frame'}
SAMPLE_SPECS2 = {'frame_material': '24-30t Unidirectional Carbon, Fast Technology', 'fork': 'Dean Aero', 'shifters': 'Shimano 105', 'front_derailleur': 'Shimano 105', 'rear_derailleur': 'Shimano 105', 'crankset': 'FSA Omega', 'chainring_sizes': '52 - 36t', 'bottom_bracket': 'PF30', 'cassette': 'Shimano 105', 'cassette_range': '11 - 30t', 'chain': 'KMC 11-speed', 'brakeset': 'Forza Stratos', 'brake_type': 'rim', 'handlebar': 'Deda Cronoero', 'stem': 'Deda Cronoero', 'seatpost': 'Dean Aero Seatpost', 'wheelset': 'Forza RC31', 'tires': 'Vittoria Zaffiro', 'recommended_use': 'triathlon', 'manufacturer_warranty': '5 years on frame'}
SAMPLE_SPECS3 = {'frame_material': 'titanium', 'fork': 'ENVE', 'fork_material': 'carbon fiber', 'headset': 'Cane Creek', 'shifters': 'Shimano Ultegra Di2 R8050', 'front_derailleur': 'Shimano Ultegra Di2 R8050', 'rear_derailleur': 'Shimano Ultegra Di2 R8050', 'crankset': 'Shimano Ultegra R8000', 'bottom_bracket': 'Shimano Ultegra BB72-41B PressFit', 'crank_arm_length': '[52cm] 170mm, [54 - 56cm] 172.5mm, [58 - 60cm] 175mm', 'cassette': '11 - 25t Shimano Ultegra R8000', 'chain': 'Shimano CN-HG701', 'brakeset': 'Shimano Ultegra R8000', 'brake_type': 'rim', 'handlebar': 'Zipp Service Course', 'handlebar_width': '[52cm] 40cm, [56 - 58cm] 100mm, [60cm] 110mm', 'bar_tape': 'PRO Classic', 'stem': 'Zipp Service Course', 'stem_length': '[52 - 54cm] 90mm, [54 - 56cm] 42cm, [58 - 60cm] 44cm', 'saddle': 'Fizik Aliante R7', 'seatpost': 'Zipp Service Course', 'wheelset': 'Mavic Ksyrium Elite UST', 'hubs': 'Mavic Instant Drive 360', 'front_axle': '9mm quick-release', 'rear_axle': '130mm quick-release', 'skewers': 'Mavic BR301', 'tires': 'Mavic Yksion', 'tire_size': '700c x 25mm', 'pedals': 'not included', 'recommended_use': 'road cycling'}


class SpecializedTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = BackCountry(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = [
            'road_bikes',
            'mountain_bikes',
            'ebikes',
            'gravel_cyclocross_bikes',
            'triathlon_tt_bikes'
        ]

        result = self._scraper._get_categories()
        print('\nCategories:', result)
        self.assertEqual(len(categories), len(result),
                         msg=f'Expected {len(categories)}; result {len(result)}')
        for key in categories:
            self.assertTrue(key in result,
                            msg=f'{key} is not in result!')

    def test_get_prods_listings(self):
        bike_type = 'road_bikes'
        bike_cats = self._scraper._get_categories()
        endpoint = bike_cats[bike_type]['href']
        soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
            endpoint), 'lxml')

        # Verify product listings fetch
        self._scraper._get_prods_on_current_listings_page(soup, bike_type)
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 1,
                        msg=f'There are {num_prods} product first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        bike_type = 'road_bikes'
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'backcountry_prods_all.csv')
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
        expected = ['site', 'product_id', 'frame_material',
                    'fork', 'cassette', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')

    def test_get_all_available_prods(self):
        expected = 24 * 5
        # Validate method
        self._scraper.get_all_available_prods()
        num_prods = len(self._scraper._products)
        # There are dupes so expect less num_prods
        self.assertTrue(num_prods > expected,
                        msg=f'expected: {expected} - found: {num_prods}')


if __name__ == '__main__':
    unittest.main()
