# python modules
import unittest
import os
from datetime import datetime
import json

from bs4 import BeautifulSoup

# package modules
from scrapers.spokes import Spokes

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
    os.path.join(HTML_PATH, 'spokes-bikes.html'))
SPECS1 = {'frame': 'Trek Custom Steel', 'fork': 'SR Suntour M-3030, coil spring, preload, 75mm travel', 'headset': '1-1/8" threadless', 'rims_wheels': 'Bontrager AT-550 36-hole alloy', 'hubs': 'Front: Formula FM21 alloy; Rear: Formula FM31 alloy', 'spokes': 'Bontrager Approved', 'tires': 'Bontrager LT3, 26x2.00"', 'crankset': 'Shimano Tourney M131', 'chainrings': '42/34/24', 'bottom_bracket': 'Sealed cartridge', 'chain': 'KMC Z51', 'front_derailleur': 'Shimano Tourney TY500', 'rear_derailleur': 'Shimano Tourney TY300', 'rear_cogs': 'Shimano TZ21 14-28, 7 speed', 'shifters': 'Shimano Tourney EF40, 7 speed', 'handlebars': 'Bontrager Riser, 25.4mm, 30mm rise', 'tape_grips': 'Bontrager SSR', 'stem': 'Bontrager alloy, 25.4mm, 25 degree', 'brakes': 'Tektro alloy linear-pull', 'pedals': 'Wellgo nylon platform', 'saddle': 'Bontrager SSR', 'seatpost': 'Bontrager SSR, 2-bolt head, 29.2mm, 12mm offset'}
SPECS2 = {'frame': 'Custom Drawn 6000 Series Aluminum', 'fork': 'Hi-Tensile Steel', 'rims_wheels': '26" double-wall 32H alloy rims', 'hubs': 'QR disc hubs, freewheel rear', 'tires': '26 x 2.125"', 'crankset': 'Alloy, 170mm w/ Chainguard', 'chainrings': '42T', 'rear_derailleur': 'Shimano Altus', 'cassette_rear_cogs': 'Shimano 13-24T 8-Speed', 'shifters': 'Shimano Altus 8-Spd Push Button', 'handlebars': 'EVO Cruiser 122 x 630mm', 'tape_grips': 'EVO Ergonomic 85mm', 'stem': 'EVO 80 Degree', 'brakes': 'Mechanical Disc, 160/140mm rotors', 'pedals': 'Rubber Cage w/ Alloy Body 9/16"', 'saddle': 'EVO Cruiser', 'seat_post': 'EVO 27.2 x 300mm', 'accessories_extras': 'Center mount kickstand, chainguard'}
SPECS3 = {'drive_system': 'Promovec 250W, 36V front hub', 'display': 'Promovec bar-mounted LED with walk-assist', 'battery_type_weight': 'Promovec 36V, 7.8Ah Li-ION smart battery', 'recharge_time': '4 hours', 'max__assisted_speed': '20 mph', 'range': '50 miles', 'frame': 'Premium reinforced eBike aluminum', 'fork': 'Full chromoly', 'headset': 'Threaded', 'rims_wheels': '700c, Alex DH19 double wall', 'hubs': 'Promovec front, Alloy rear', 'tires': 'Kenda, 700 x 40c', 'crankset': 'Prowheel 170mm', 'chainrings': '44T', 'rear_derailleur': 'Shimano Tourney TY-500', 'cassette_rear_cogs': 'Shimano TZ21, 7-speed, 14-28T', 'shifters': 'MicroShift Twist Shifter', 'handlebars': 'Alloy riser, 660mm', 'tape_grips': 'Comfort, 135/92mm', 'stem': 'Promax adjustable', 'brakes': 'Tektro 855AL v-brakes', 'pedals': 'Polished alloy with rubber tread', 'saddle': 'SR Freeway', 'seatpost': 'Alloy 27.2 x 300mm', 'accessories_extras': 'Rear mounted rack for battery, heavy-duty center mount kickstand'}


class CityBikesTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Spokes(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = [
            'road_bikes',
            'mountain_bikes',
            'cyclocross',
            'commuter_urban',
            'comfort',
            'cruiser',
            'fitness',
            'electric',
            'hybrid_bike',
            'childrens',
            'other',
            'bmx'
        ]

        result = self._scraper._get_categories()
        print('\nCategories:', result)
        for key in result.keys():
            self.assertTrue(key in categories,
                            msg=f'{key} not in {categories}')

    def test_get_prods_listing(self):
        bike_type = 'road_bikes'
        self._scraper._page_size = 30  # constrain maximum num of prods on page
        categories = self._scraper._get_categories()
        endpoint = categories[bike_type]['href']
        soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
            endpoint), 'lxml')

        # Verify product listings fetch
        self._scraper._get_prods_on_current_listings_page(soup, bike_type)
        num_prods = len(self._scraper._products)
        expected_num_prods = int(categories[bike_type]['count'])
        if expected_num_prods > self._scraper._page_size:
            self.assertEqual(num_prods, self._scraper._page_size,
                             msg=f'{num_prods} product, expected: {self._scraper._page_size}.')
        else:
            self.assertEqual(expected_num_prods, num_prods,
                             msg=f'{num_prods} product, expected: {expected_num_prods}.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        bike_type = 'road_bikes'
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'spokes_prods_all.csv')
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
                    'fork', 'cassette_rear_cogs', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
