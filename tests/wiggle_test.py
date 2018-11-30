# python modules
import unittest
import os
from bs4 import BeautifulSoup
from datetime import datetime

# package modules
from scrapers.wiggle import Wiggle

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
TEST_PROD_LISTING_PATH = os.path.join(TEST_DATA_PATH, 'performance_prod_listing_test_data.csv')
SHOP_BIKES_HTML_PATH = os.path.abspath(os.path.join(HTML_PATH, 'wiggle.html'))
PINARELLO_SPECS = {
    'frame_material': 'Toray T1100 1K Dream Carbon Fiber',
    'fork': 'Onda',
    'fork_material': 'Toray T1100 1K Dream Carbon Fiber',
    'headset': '1-1/8 - 1-1/2 in',
    'shifters': 'SRAM Red eTap',
    'front_derailleur': 'SRAM Red eTap',
    'rear_derailleur': 'SRAM Red eTap',
    'crankset': '53 / 39 t SRAM Red GXP, 52 / 36 t SRAM Red GXP, 50 / 34 t SRAM Red GXP',
    'bottom_bracket': '[shell] Italian threaded, [adapter] SRAM GXP Team',
    'crank_arm_length': '170 mm, 172.5 mm, 175 mm',
    'cassette': '11 - 25 t SRAM XG-1190',
    'chain': 'SRAM PC-Red',
    'brakeset': 'SRAM Red Aero Link',
    'brake_type': 'rim',
    'handlebar': 'Zipp SL-70 Aero Carbon',
    'handlebar_width': '[42cm, 44cm, 46.5cm] 38 cm, [50cm, 51.5cm] 40 cm, [sizes 53cm, 54cm] 42 cm, [sizes 55cm, 56cm, 57.5cm, 59.5cm, 62cm] 44 cm',
    'bar_tape': 'Arundel cork',
    'stem': 'Zipp SL Sprint Carbon',
    'saddle': 'Fizik Aliante R7',
    'seatpost': 'Dogma Aero',
    'seat_collar': 'TwinForce (integrated)',
    'wheelset': 'Zipp 404 NSW Carbon Clincher',
    'hubs': 'Zipp Cognition',
    'skewers': '9mm quick-release',
    'tires': 'Vittoria Corsa G Plus',
    'tire_size': '700 c x 25 mm',
    'pedals': 'not included',
    'recommended_use': 'cycling',
    'manufacturer_warranty': '2 years on frame'
    }
RIDLEY_SPECS = {
    'frame_material': '30t and 24t high-modulus carbon fiber',
    'fork': 'Oryx Disc 12TA, carbon steerer',
    'fork_material': 'carbon fiber',
    'shifters': 'Shimano ST-R685',
    'front_derailleur': 'Shimano Ultegra 6800',
    'rear_derailleur': 'Shimano Ultegra 6800',
    'crankset': '46 / 36 t Shimano Ultegra 6800',
    'bottom_bracket': 'PF30',
    'cassette': '11 - 28 t Shimano 105 5800',
    'chain': 'KMC X11',
    'brakeset': 'Shimano BR-RS805/BR-RS785 Hydraulic',
    'rotors': '[front] 60 mm, [rear] 140 mm',
    'handlebar': '4ZA Cirrus E.2',
    'stem': '4ZA Cirrus',
    'saddle': '4ZA Cirrus Pro Cr/Ti rails',
    'seatpost': '4ZA Cirrus Carbon 27.2 x 350mm',
    'wheelset': 'DT Swiss R23 Spline DB',
    'front_axle': '12TA',
    'tires': 'Clement MXP Tubeless Ready',
    'tire_size': '700 c x 33 mm',
    'pedals': 'not included',
    'recommended_use': 'cyclocross',
    'manufacturer_warranty': '5 years on frame'
}


class WiggleTestCase(unittest.TestCase):
    def setUp(self):
        self.wiggle = Wiggle(save_data_path=DATA_PATH)

    def test_fetch_prod_listing_view(self):
        text = self.wiggle._fetch_prod_listing_view()
        soup = BeautifulSoup(text, 'lxml')
        self.wiggle._get_prods_on_current_listings_page(soup)
        self.assertEqual(self.wiggle._page_size, len(self.wiggle._products))

    #FIXME - complete this unit test snippet (FYI - long running)
    def test_get_bike_urls(self):
        response = self.wiggle.get_all_available_prods()
        self.assertEqual(False, response)

    def test_get_max_num_prods(self):
        # load test html into memory
        with open(SHOP_BIKES_HTML_PATH, encoding='utf-8') as f:
            prod_list_text = f.read()

        prod_list_soup = BeautifulSoup(prod_list_text, 'lxml')

        expected = 352  # from html file: 352 bikes
        result = self.wiggle._get_max_num_prods(prod_list_soup)
        self.assertEqual(expected, result)

    # FIXME: finish this unit test logic has preformance data not competitive
    def test_get_prods_on_page(self):
        cases = {
            "Fuji Absolute 1.9 Disc Flat Bar Road Bike -2018":
                {'href': '/shop/bikes-frames/fuji-absolute-19-disc-flat-bar-road-bike-2018-31-8559', 'desc': 'Fuji Absolute 1.9 Disc Flat Bar Road Bike -2018', 'price': '$449.99', 'msrp': '$499.99', 'id': '7000000000000008209'},
            "Breezer Cloud 9 Carbon 29er Mountain Bike - 2018": {'href': '/shop/bikes-frames/breezer-cloud-9-carbon-29er-mountain-bike-2018-31-8578', 'desc': 'Breezer Cloud 9 Carbon 29er Mountain Bike - 2018', 'price': '$1,499.99', 'msrp': '$2,999.99', 'id': '7000000000000006408'},
            "Marin Hawk Hill 27.5 Mountain Bike - 2018": {'href': '/shop/bikes-frames/marin-hawk-hill-275-mountain-bike-2018-31-6715', 'desc': 'Marin Hawk Hill 27.5 Mountain Bike - 2018', 'price': '$1,399.99', 'msrp': '$1,499.99', 'id': '1215816'},
            "Fuji Finest 1.0 LE Women's Road Bike - 2017": {'href': '/shop/bikes-frames/fuji-finest-10-le-womens-road-bike-2017-31-5619', 'desc': "Fuji Finest 1.0 LE Women's Road Bike - 2017", 'price': '$799.97', 'msrp': '$1,349.00', 'id': '1208310'}
        }

        # load test html into memory
        with open(SHOP_BIKES_HTML_PATH, encoding='utf-8') as f:
            prod_list_text = f.read()

        prod_list_soup = BeautifulSoup(prod_list_text, 'lxml')
        self.wiggle._get_prods_on_current_listings_page(prod_list_soup)
        self.assertEqual(self.wiggle._page_size, len(self.wiggle._products))
        for key in cases:
            self.assertTrue(key in self.wiggle._products)
        for value in cases.values():
            self.assertTrue(value in self.wiggle._products.values())

    def test_get_prod_listings(self):
        self.wiggle.get_all_available_prods(to_csv=True)
        self.assertTrue(self.wiggle._num_bikes, len(self.wiggle._products))

    #TODO - implement per Wiggle scope
    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(HTML_PATH,
            'Pinarello F10 Dura-Ace Di2 Complete Road Bike - 2018 _ Competitive Cyclist.html'))
        with open(html_path, encoding='utf-8') as f:            
            pinarello_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(HTML_PATH,
            'Ridley X-Night Disc Rival 1 Complete Cyclocross Bike - 2018 _ Competitive Cyclist.html'))
        with open(html_path, encoding='utf-8') as f:
            ridley_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(HTML_PATH, 'bike-eli-elliptigo-sub-31-8914.html'))
        with open(html_path, encoding='utf-8') as f:
            generic_error = f.read()

        marin_detail_soup = BeautifulSoup(pinarello_prod_detail_text, 'lxml')
        bkestrel_detail_soup = BeautifulSoup(ridley_prod_detail_text,
                                                  'lxml')
        generic_error_soup = BeautifulSoup(generic_error, 'lxml')

        # case 1: exact match per example data
        result = self.wiggle._parse_prod_specs(marin_detail_soup)
        self.assertEqual(len(PINARELLO_SPECS), len(result))
        for key in PINARELLO_SPECS.keys():
            self.assertEqual(PINARELLO_SPECS[key], result[key])

        # case 2: using second data, exact match in components
        result = self.wiggle._parse_prod_specs(bkestrel_detail_soup)
        self.assertEqual(len(RIDLEY_SPECS), len(result))
        for key in RIDLEY_SPECS.keys():
            self.assertEqual(RIDLEY_SPECS[key], result[key])

        # case 3: safely handle error
        result = self.wiggle._parse_prod_specs(generic_error_soup)
        self.assertEqual(0, len(result))


if __name__ == '__main__':
    unittest.main()
