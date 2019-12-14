# python modules
import unittest
import os
from datetime import datetime
import json

from bs4 import BeautifulSoup

# package modules
from scrapers.citybikes import CityBikes

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
    os.path.join(HTML_PATH, 'citybikes.html'))
COMMUTER_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'citybikes-Commuter_Urban.html')
)
DRAGONFLY_SPECS = {
    'frame': 'Reynolds 853 chromoly, w/dropper post routing, ISCG05, sliding 12x142mm dropouts',
    'fork': 'Fox 32 Float Performance Series, 120mm-travel w/tapered steerer, 15mm thru-axle',
    'rims_wheels': 'WTB Frequency Team i23 TCS',
    'hubs': 'Formula disc',
    'spokes': 'Stainless-steel',
    'tires': 'Vittoria Barzo, 27.5 x 2.25',
    'crankset': 'Shimano',
    'chainrings': '36/22',
    'front_derailleur': 'Shimano Deore',
    'rear_derailleur': 'Shimano SLX Shadow',
    'rear_cogs': 'Shimano, 10-speed: 11-36',
    'shifters': 'Shimano SLX',
    'handlebars': 'Ritchey Trail',
    'tape_grips': 'Jamis lock-on',
    'stem': 'Ritchey Trail',
    'brakes': 'Shimano Deore disc, 180/160mm rotors',
    'saddle': 'WTB Volt Comp w/Luxe Zone Cut-Out',
    'seatpost': 'Ritchey Trail'}
CROSS_TRAIL_SPECS = {
    'frame': 'Specialized A1 Premium Aluminum, Fitness Geometry, butted tubing, rack mounts, Plug + Play fender mounts',
    'fork': 'SR Suntour NEX w/ Specialized Fitness Brain technology, 55mm of travel, 1-1/8" steerer, QR, fender mounts',
    'rims_wheels': '700C disc, double wall',
    'tires': 'Trigger Sport Reflect, 60 TPI, wire bead, 700x38mm',
    'crankset': 'Shimano Tourney, 3-piece',
    'chainrings': '48/38/28T',
    'bottom_bracket': 'BSA, 68mm, square taper',
    'chain': 'KMC X8EPT, 8-speed, anti-corrosion coating w/ reusable Missing Link',
    'front_derailleur': 'Shimano Tourney, top swing, 31.8mm clamp',
    'rear_derailleur': 'Shimano Altus, 8-Speed',
    'cassette_rear_cogs': 'Sunrace, 8-speed, 11-34t',
    'shifters': 'Shimano Altus, RapidFire Plus, w/ gear display',
    'handlebars': 'Double-butted alloy, 9-degree backsweep, 31.8mm',
    'tape_grips': 'Specialized Body Geometry XCT, lock-on',
    'stem': '3D forged alloy, 7-degree rise, 31.8mm clamp',
    'brakes': 'Promax Solve, hydraulic disc, post mount, 160mm rotor',
    'saddle': 'Specialized Canopy Comp, hollow Cr-Mo rails, 155mm',
    'seat_post': 'Alloy, 12mm offset, 2-bolt clamp, 27.2mm'}


class CityBikesTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = CityBikes(save_data_path=DATA_PATH)

    def test_fetch_prod_listing_view(self):
        text = self._scraper._fetch_prod_listing_view(page_size=30)
        soup = BeautifulSoup(text, 'lxml')
        self._scraper._get_prods_on_current_listings_page(
            soup, bike_type='all')
        self.assertEqual(30, len(self._scraper._products),
                         msg='First page should return 30 products.')

    def test_get_categories(self):
        categories = ['road', 'mountain', 'commuter_urban', 'comfort',
                      'fitness', 'hybrid', 'childrens',
                      'other', 'cyclocross']

        result = self._scraper._get_categories()
        print('\nCategories:', result)
        for key in result.keys():
            self.assertTrue(key in categories,
                            msg=f'{key} not in {categories}')

    def test_get_prods_listing(self):
        bike_type = 'road'
        bike_cats = self._scraper._get_categories()
        qs = '&rb_ct=' + str(bike_cats[bike_type]['filter_val'])
        soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
            qs=qs), 'lxml')

        # Verify product listings fetch
        self._scraper._get_prods_on_current_listings_page(soup, bike_type)
        num_prods = len(self._scraper._products)
        expected_num_prods = int(bike_cats[bike_type]['count'])
        if expected_num_prods > self._scraper._page_size:
            self.assertEqual(num_prods, self._scraper._page_size,
                             msg=f'{num_prods} product, expected: {self._scraper._page_size}.')
        else:
            self.assertEqual(expected_num_prods, num_prods,
                             msg=f'{num_prods} product, expected: {expected_num_prods}.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        bike_type = 'road'
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'citybikes_prods_all.csv')
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

    def test_get_all_available_prods(self):
        result = self._scraper.get_all_available_prods()

        total_bikes = 0
        text = self._scraper._fetch_prod_listing_view(page_size=30)
        soup = BeautifulSoup(text, 'lxml')
        for values in self._scraper._get_categories(soup).values():
            total_bikes += values['count']
        num_prods = len(self._scraper._products)
        # There are dupes so expect less num_prods
        self.assertTrue(total_bikes >= num_prods,
                        msg=f'expected: {total_bikes} - found: {num_prods}')


if __name__ == '__main__':
    unittest.main()
