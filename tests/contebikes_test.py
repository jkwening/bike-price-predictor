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
        self._conte = ConteBikes(save_data_path=DATA_PATH)

    def test_fetch_prod_listing_view(self):
        text = self._conte._fetch_prod_listing_view(
            endpoint=self._conte._PROD_PAGE_ENDPOINT, page_size=30)
        soup = BeautifulSoup(text, 'lxml')
        self._conte._get_prods_on_current_listings_page(
            soup, bike_type='all')
        self.assertEqual(30, len(self._conte._products),
                         msg='First page should return 30 products.')

    def test_get_categories(self):
        categories = {
            'road_bikes': {'filter_par': 'rb_ct', 'filter_val': 1001, 'count':
                407},
            'mountain_bikes': {'filter_par': 'rb_ct', 'filter_val': 1006, 'count':
                446},
            'cyclocross': {'filter_par': 'rb_ct', 'filter_val': 1014,
                               'count': 57},
            'commuter_urban': {'filter_par': 'rb_ct', 'filter_val': 1017,
                               'count': 226},
            'comfort': {'filter_par': 'rb_ct', 'filter_val': 1020, 'count':
                64},
            'cruiser': {'filter_par': 'rb_ct', 'filter_val': 1021, 'count':
                90},
            'fitness_bikes': {'filter_par': 'rb_ct', 'filter_val': 1243,
                              'count':
                136},
            'electric_bicycles': {'filter_par': 'rb_ct', 'filter_val': 1038,
                              'count':
                74},
            'hybrid_bikes': {'filter_par': 'rb_ct', 'filter_val': 1022, 'count':
                155},
            'kids_bikes': {'filter_par': 'rb_ct', 'filter_val': 1023, 'count':
                84},
            'other': {'filter_par': 'rb_ct', 'filter_val': 1037, 'count':
                5},
            'bmx': {'filter_par': 'rb_ct', 'filter_val': 1032, 'count':
                17}
        }

        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result = self._conte._get_categories(soup)
        for title in categories.keys():
            cat = categories[title]
            r_cat = result[title]
            for key in cat.keys():
                self.assertTrue(cat[key] == r_cat[key],
                                msg=f'{title}-{key}: result={r_cat[key]} - '
                                    f'expected:'
                                    f'{cat[key]}')

    def test_get_prod_listings(self):
        with open(ROAD_BIKES_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        self._conte._get_prods_on_current_listings_page(
            soup, 'road_bikes')
        self.assertEqual(30, len(self._conte._products),
                         msg='First page should return 30 products.')

    def test_get_all_available_prods(self):
        result = self._conte.get_all_available_prods()

        total_bikes = 0
        for values in self._conte._BIKE_CATEGORIES.values():
            total_bikes += values['count']
        num_prods = len(self._conte._products)
        # There are dupes so expect less num_prods
        self.assertTrue(total_bikes >= num_prods,
                        msg=f'expected: {total_bikes} - found: {num_prods}')

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'conte-Cannondale-Trail.html'))
        with open(html_path, encoding='utf-8') as f:
            cannondale_trail_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'conte-Giant-Defy.html'))
        with open(html_path, encoding='utf-8') as f:
            giant_defy_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'conte-Specialized-Boys-Hotwalk.html'))
        with open(html_path, encoding='utf-8') as f:
            generic_error = f.read()

        cannondale_trail_detail_soup = BeautifulSoup(
            cannondale_trail_prod_detail_text, 'lxml')
        giant_defy_detail_soup = BeautifulSoup(
            giant_defy_prod_detail_text, 'lxml')
        generic_error_soup = BeautifulSoup(generic_error, 'lxml')

        # case 1: exact match per example data
        result = self._conte._parse_prod_specs(cannondale_trail_detail_soup)
        self.assertEqual(len(CANNONDALE_TRAIL_SPECS), len(result))
        for key in CANNONDALE_TRAIL_SPECS.keys():
            self.assertEqual(
                CANNONDALE_TRAIL_SPECS[key], result[key])

        # case 2: using second data, exact match in components
        result = self._conte._parse_prod_specs(giant_defy_detail_soup)
        self.assertEqual(len(GIANT_DEFY_SPECS), len(result))
        for key in GIANT_DEFY_SPECS.keys():
            self.assertEqual(GIANT_DEFY_SPECS[key], result[key])

        # case 3: safely handle missing specs
        result = self._conte._parse_prod_specs(generic_error_soup)
        self.assertEqual(0, len(result))


if __name__ == '__main__':
    unittest.main()
