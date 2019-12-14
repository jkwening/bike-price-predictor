# python modules
import unittest
import os
from datetime import datetime

from bs4 import BeautifulSoup

# package modules
from scrapers.contebikes import ConteBikes

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
    os.path.join(HTML_PATH, 'conte.html'))
ROAD_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'conte-Road-Bikes.html')
)
GIANT_DEFY_SPECS = {
    'frame': 'Advanced-grade composite',
    'fork': 'Advanced-grade composite, Hybrid OverDrive steerer',
    'rims_wheels': 'Giant PR-2 Disc, Tubeless',
    'hubs': 'Giant Performance Tracker Road Disc, Sealed Bearings, 12mm axles, 28h',
    'spokes': 'Sapim Race 14/15g',
    'tires': 'Giant Gavia AC 1 Tubeless, 700x25, Folding',
    'crankset': 'Shimano FC-R510',
    'chainrings': '34/50',
    'bottom_bracket': 'Shimano, Press Fit',
    'chain': 'KMC X11EL-1',
    'front_derailleur': 'Shimano 105',
    'rear_derailleur': 'Shimano 105',
    'cassette_rear_cogs': 'Shimano 105 11x32, 11-Speed',
    'shifters': 'Shimano 105',
    'handlebars': 'Giant Contact, 31.8mm',
    'stem': 'Giant Connect',
    'brake_levers': 'Shimano 105',
    'brakes': 'Giant Conduct, hydraulic disc, 140mm',
    'pedals': 'N/A',
    'saddle': 'Contact Neutral',
    'seat_post': 'Giant D-Fuse composite'}
CANNONDALE_TRAIL_SPECS = {
    'frame': 'Trail, SmartForm C2 Alloy, SAVE, 1-1/8” head tube',
    'fork': 'SR Suntour XCM, 100mm, Coil, 51mm offset',
    'headset': 'Sealed Semi Integrated, 1-1/8 reducer',
    'axles': 'Front: QR',
    'rims_wheels': 'WTB SX19, 32h',
    'hubs': 'Formula w/ HG driver',
    'spokes': 'Stainless Steel, 14g',
    'tires': 'WTB Ranger Comp, 27.5/29 x 2.25" DNA Compound',
    'crankset': 'FSA Comet, Alpha Drive',
    'chainrings': '36/22',
    'bottom_bracket': 'Sealed Bearing BSA',
    'chain': 'KMC HG53, 9-speed',
    'front_derailleur': 'MicroShift Direct Mount',
    'rear_derailleur': 'Shimano Altus',
    'cassette_rear_cogs': 'Sunrace, 11-36, 9-speed',
    'shifters': 'Shimano Easy Fire EF505, 2x9',
    'handlebars': 'Cannondale C4 Riser, 6061 Alloy, 25mm rise, 8° sweep, 6° rise, 720mm',
    'tape_grips': 'Cannondale Dual-Density',
    'stem': 'Cannondale C4, 3D Forged 6061 Alloy, 1-1/8", 31.8, 7°',
    'brake_levers': 'Shimano MT200 hydro disc',
    'brakes': 'Shimano MT200 hydro disc, 160/160mm RT26 rotors',
    'pedals': 'Cannondale Platform',
    'saddle': 'Cannondale Stage 3',
    'seat_post': 'Cannondale C4, 6061 Alloy, 31.6 x 400mm'}


class ConteBikesTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = ConteBikes(save_data_path=DATA_PATH)

    def test_fetch_prod_listing_view(self):
        text = self._scraper._fetch_prod_listing_view(page_size=30)
        soup = BeautifulSoup(text, 'lxml')
        self._scraper._get_prods_on_current_listings_page(
            soup, bike_type='all')
        self.assertEqual(30, len(self._scraper._products),
                         msg='First page should return 30 products.')

    def test_get_categories(self):
        categories = [
            'road_bikes',
            'mountain_bikes',
            'cyclocross',
            'commuter_urban',
            'comfort',
            'cruiser',
            'fitness_bikes',
            'electric_bicycles',
            'hybrid_bikes',
            'kids_bikes',
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
        bike_type = 'road_bikes'
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'contebikes_prods_all.csv')
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
        for values in self._scraper._get_categories().values():
            total_bikes += values['count']
        num_prods = len(self._scraper._products)
        # There are dupes so expect less num_prods
        self.assertTrue(total_bikes >= num_prods,
                        msg=f'expected: {total_bikes} - found: {num_prods}')


if __name__ == '__main__':
    unittest.main()
