# python modules
import unittest
import os
from datetime import datetime

from bs4 import BeautifulSoup

# package modules
from scrapers.litespeed import LiteSpeed

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
SHOP_ROAD_HTML_PATH = os.path.abspath(os.path.join(
    HTML_PATH, 'litespeed-roadbikes.html'))
SAMPLE_SPECS1 = [{'headset': 'Cane Creek 40 Series', 'stem': '3T ARX II Pro', 'handlebar': '3T Ernova Pro', 'bar_tape': 'Prologo Black', 'seatpost': 'FSA SLK Carbon', 'saddle': 'Fizik', 'shifters': 'Ultegra Di2', 'rotors': 'Shimano RT800 160mm', 'front_derailleur': 'Ultegra Di2', 'rear_derailleur': 'Ultegra Di2', 'crankset': 'Ultegra 50/34', 'cassette': 'Ultegra 11-30', 'chain': 'Shimano HG701', 'bottom_bracket': 'Praxis', 'tires': 'Continental Gatorskin 700x25', 'wheelset': 'Select Wheels Above', 'brakeset': 'Ultegra', 'fork': 'Litespeed Carbon', 'bike_sub_type': 'Ultegra Di2'}, {'headset': 'Cane Creek 40 Series', 'stem': '3T ARX II Pro', 'handlebar': '3T Ernova Pro', 'bar_tape': 'Prologo Black', 'seatpost': 'FSA SLK Carbon', 'saddle': 'Fizik', 'shifters': 'Ultegra', 'rotors': 'Shimano RT800 160mm', 'front_derailleur': 'Ultegra', 'rear_derailleur': 'Ultegra', 'crankset': 'Ultegra 50/34', 'cassette': 'Ultegra 11-30', 'chain': 'Shimano HG701', 'bottom_bracket': 'Praxis', 'tires': 'Continental Gatorskin 700x25', 'wheelset': 'Select Wheels Above', 'brakeset': 'Ultegra', 'fork': 'Litespeed Carbon', 'bike_sub_type': 'Ultegra'}]
SAMPLE_SPECS2 = [{'headset': 'Chris King InSet 7 Matte Black', 'stem': '3T ARX II Team Stealth', 'handlebar': '3T Ernova Team Stealth', 'bar_tape': 'Prologo Black', 'seatpost': 'Litespeed Titanium', 'saddle': 'WTB Volt Team 142 Cromo with Ti Rails', 'shifters': 'Dura-Ace Di2 Shift/Hydraulic Disc', 'rotors': 'Shimano RT900 160mm', 'front_derailleur': 'Dura-Ace Di2 R9150', 'rear_derailleur': 'Dura-Ace Di2 R9150', 'crankset': 'Praxis Zayante Carbon 48-32', 'cassette': 'Dura-Ace R9150 11-30', 'chain': 'Dura-Ace', 'bottom_bracket': 'Praxis PF30', 'wheelset': 'Select Wheels Above', 'brakeset': 'Dura-Ace', 'fork': 'Litespeed Carbon', 'bike_sub_type': 'Dura-Ace Di2'}]
SAMPLE_SPECS3 = [{'headset': 'Cane Creek 40 Series Tapered', 'stem': 'Evolve XC 31.8mm, 90x6', 'handlebar': 'Respond Low Riser 785mm', 'bar_tape': 'ESI Chunky Black', 'seatpost': 'Turbine 31.6x400 Black', 'saddle': 'WTB Volt Team 142 Cromo', 'rear_shifter': 'GX Eagle Trigger Shifter, 12 speed rear', 'rotors': 'CenterLine 180mm, 6-bolt', 'rear_derailleur': 'GX Eagle 12 speed', 'crankset': 'Praxis Cadet M32 175', 'cassette': 'XG-1275 GX Eagle 10-50, 12 speed', 'chain': 'GX Eagle 12 speed', 'bottom_bracket': 'Praxis M30', 'front_tire': 'Maxxis Ikon 29x2.35 Tubeless', 'rear_tire': 'Maxxis Ikon 29x2.35 Tubeless', 'wheelset': 'Select Wheels Above', 'brakes': 'Level TL Disc Brake', 'fork': 'Fox Factory Float 34, 29/27.5+ Boost 120mm Fit 4', 'bike_sub_type': 'SRAM GX Eagle 29'}, {'headset': 'Cane Creek 40 Series Tapered', 'stem': 'Evolve XC 31.8mm, 90x6', 'handlebar': 'Respond Low Riser 785mm', 'bar_tape': 'ESI Chunky Black', 'seatpost': 'Turbine 31.6x400 Black', 'saddle': 'WTB Volt Team 142 Cromo', 'rear_shifter': 'GX Eagle Trigger Shifter, 12 speed rear', 'rotors': 'CenterLine 180mm, 6-bolt', 'rear_derailleur': 'GX Eagle 12 speed', 'crankset': 'Praxis Cadet M32 175', 'cassette': 'XG-1275 GX Eagle 10-50, 12 speed', 'chain': 'GX Eagle 12 speed', 'bottom_bracket': 'Praxis M30', 'front_tire': 'Maxxis Rekon 27.5x2.8 EXO/TR Tubeless', 'rear_tire': 'Maxxis Ikon+ 27.5x2.8 EXO/TR Tubeless', 'wheelset': 'Select Wheels Above', 'brakes': 'Level TL Disc Brake', 'fork': 'Fox Factory Float 34, 29/27.5+ Boost 120mm Fit 4', 'bike_sub_type': 'SRAM GX Eagle 27.5+'}]


class SpecializedTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = LiteSpeed(save_data_path=DATA_PATH)

    def test_get_prods_listings(self):
        bike_type = 'road'
        endpoint = self._scraper._CATEGORIES[bike_type]
        soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
            endpoint), 'lxml')

        # Verify product listings fetch
        self._scraper._get_prods_on_current_listings_page(soup, bike_type)
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 5,
                        msg=f'There are {num_prods} product first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        bike_type = 'road'
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'litespeed_prods_all.csv')
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
        expected = ['site', 'product_id', 'shifters',
                    'fork', 'cassette', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')

    def test_get_all_available_prods(self):
        expected = 36
        # Validate method
        self._scraper.get_all_available_prods()
        num_prods = len(self._scraper._products)
        # There are dupes so expect less num_prods
        self.assertTrue(num_prods > expected,
                        msg=f'expected: {expected} - found: {num_prods}')


if __name__ == '__main__':
    unittest.main()
