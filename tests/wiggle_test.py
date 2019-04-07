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
KIDDIMOTO_SPECS = {
    'wheel_size': '12" (203)'
    }
ORRO_SPECS = {
    'frame': 'Orro Pyro Carbon Disc Brake Frame',
    'fork': 'Orro Superlight 2.0 Full Carbon Disc Brake',
    'brake_shift_levers': 'Shimano 105 R7000',
    'brakes': 'TRP Spyre mechanical disc brake, flat mount. Shimano Shimano 105 R7000 levers',
    'derailleur': 'Shimano 105 R7000',
    'cassette': 'Shimano 105 R7000, 11-28T',
    'chainset': 'FSA Omega, 50/34T',
    'wheelset': 'Fulcrum Racing 600 DB',
    'tyres': 'Continental Grand Sport Race 25C',
    'fork_material': 'Carbon',
    'bottle_cage_mounts': 'Double',
    'groupset_manufacturer': 'Shimano',
    'chainset_type': 'Double',
    'tires': 'Continental Grand Sport Race 25C',
    'brake_type': 'Hydraulic Disc Brake',
    'bar_tape_grips': 'Token Lock On',
    'handlebars': 'FSA Vero Compact',
    'stem': 'Integrated',
    'seat_post': 'Orro Superlite Alloy',
    'saddle': 'Prologo Kappa RS',
    'model_year': '2019',
    'road': 'Yes'
    }
VITUS_SPECS = {
    'weight': '7.9kg',
    'frame': 'Carbon',
    'fork': 'Carbon',
    'fork_material': 'Carbon',
    'steerer': 'Tapered 1 1/8 - 1 1/2',
    'bottle_cage_mounts': 'Double',
    'cable_routing': 'External',
    'mudguard_mounts': 'Yes',
    'rear_rack_mounts': 'Yes',
    'groupset_manufacturer': 'Shimano',
    'number_of_gears': '22 Speed',
    'chainset': 'Shimano Ultegra',
    'chainset_type': 'Double',
    'chain': 'KMC X11L',
    'cassette': 'Shimano Ultegra',
    'wheel_size': '700c (622)',
    'tires': 'Mavic Yksion Pro',
    'brake_type': 'Hydraulic Disc Brake',
    'brakes': 'Shimano Ultegra R8020',
    'brake_calipers': 'Shimano Ultegra R8020',
    'handlebars': 'Ritchey Comp Streem II',
    'stem': 'Ritchey Comp 4 Axis',
    'seat_post': 'Prime carbon',
    'saddle': 'Fizik Antares R5',
    'model_year': '2018',
    'bike_weight': '7.9kg / 17.41 lbs',
    'road': 'Yes'
    }


class WiggleTestCase(unittest.TestCase):
    def setUp(self):
        self.wiggle = Wiggle(save_data_path=DATA_PATH)

    def test_fetch_prod_listing_view(self):
        text = self.wiggle._fetch_prod_listing_view()
        soup = BeautifulSoup(text, 'lxml')
        self.wiggle._get_prods_on_current_listings_page(soup)
        self.assertEqual(self.wiggle._page_size, len(self.wiggle._products))

    def test_get_max_num_prods(self):
        # load test html into memory
        with open(SHOP_BIKES_HTML_PATH, encoding='utf-8') as f:
            prod_list_text = f.read()

        prod_list_soup = BeautifulSoup(prod_list_text, 'lxml')

        expected = 352  # from html file: 352 bikes
        result = self.wiggle._get_max_num_prods(prod_list_soup)
        self.assertEqual(expected, result)

    def test_get_prods_on_page(self):
        # load test html into memory
        with open(SHOP_BIKES_HTML_PATH, encoding='utf-8') as f:
            prod_list_text = f.read()

        prod_list_soup = BeautifulSoup(prod_list_text, 'lxml')
        self.wiggle._get_prods_on_current_listings_page(prod_list_soup)
        self.assertEqual(self.wiggle._page_size, len(self.wiggle._products))

    def test_get_prod_listings(self):
        self.wiggle.get_all_available_prods(to_csv=True)
        self.assertTrue(self.wiggle._num_bikes, len(self.wiggle._products))

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(HTML_PATH,
            'wiggle-Kiddimoto-Balance-Bikes.html'))
        with open(html_path, encoding='utf-8') as f:            
            kiddimoto_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(HTML_PATH,
            'wiggle-Orro-PYRO-Disc-Road-Bikes.html'))
        with open(html_path, encoding='utf-8') as f:
            orro_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(HTML_PATH,
            'wiggle-Vitus-Vitesse-Road-Bike.html'))
        with open(html_path, encoding='utf-8') as f:
            vitus_prod_detail_text = f.read()

        # html_path = os.path.abspath(os.path.join(HTML_PATH, 'bike-eli-elliptigo-sub-31-8914.html'))
        # with open(html_path, encoding='utf-8') as f:
        #     generic_error = f.read()

        kiddimoto_detail_soup = BeautifulSoup(kiddimoto_prod_detail_text, 'lxml')
        orro_detail_soup = BeautifulSoup(orro_prod_detail_text,
                                                  'lxml')
        vitus_detail_soup = BeautifulSoup(vitus_prod_detail_text, 'lxml')
        # generic_error_soup = BeautifulSoup(generic_error, 'lxml')

        # case 1: exact match per example data
        result = self.wiggle._parse_prod_specs(kiddimoto_detail_soup)
        self.assertEqual(len(KIDDIMOTO_SPECS), len(result))
        for key in KIDDIMOTO_SPECS.keys():
            self.assertEqual(KIDDIMOTO_SPECS[key], result[key])

        # case 2: using second data, exact match in components
        result = self.wiggle._parse_prod_specs(orro_detail_soup)
        self.assertEqual(len(ORRO_SPECS), len(result))
        for key in ORRO_SPECS.keys():
            self.assertEqual(ORRO_SPECS[key], result[key])

        # case 3: using third data, exact match in components
        result = self.wiggle._parse_prod_specs(vitus_detail_soup)
        self.assertEqual(len(VITUS_SPECS), len(result))
        for key in VITUS_SPECS.keys():
            self.assertEqual(VITUS_SPECS[key], result[key])

        # # case 4: safely handle error TODO
        # result = self.wiggle._parse_prod_specs(generic_error_soup)
        # self.assertEqual(0, len(result))


if __name__ == '__main__':
    unittest.main()
