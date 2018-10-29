# python modules
import unittest
import os
from bs4 import BeautifulSoup
from datetime import datetime

# package modules
from scrapers.performance_bike import PerformanceBikes

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
TEST_PROD_LISTING_PATH = os.path.join(TEST_DATA_PATH, 'performance_prod_listing_test_data.csv')
SHOP_BIKES_HTML_PATH = os.path.abspath(os.path.join(HTML_PATH, 'performance_bike_shop_bikes.html'))
MARIN_SPECS = {
    'Bottom Bracket': 'External seal cartridge bearing',
    'Brakes': 'Shimano BR-M315 hydraulic disc, 180mm/160mm rotor',
    'Cassette': 'Sunrace 10-speed, 11-42T',
    'Chain': 'KMC X10',
    'Crankset': 'Marin Forged Alloy 1x10, 32T, 76 BCD',
    'Fork': 'RockShox Recon Silver RL 27.5" fork, 120mm travel, '
            'compression and rebound adjustment, alloy tapered steerer,'
            ' 15mm thru axle',
    'Frame': 'Series 3 6061 aluminum frame, 27.5" wheels, 120mm travel '
             'MultiTrac suspesnion, 135mm QR',
    'Front Derailleur': 'N/A',
    'Grips/Tape': 'Marin Dual Density',
    'Handlebar': 'Marin mini riser, 15mm rise, 780mm width',
    'Headset': 'FSA Orbit',
    'Levers': 'Shimano BR-M315',
    'Pedals': 'N/A',
    'Rear Derailleur': 'Shimano Deore Shadow Plus, 10-speed',
    'Rear Shock': 'X Fusion O2 Pro R, 190x50mm, 120mm travel, Tube-B',
    'Saddle': 'Marin Speed Concept',
    'Seatpost': 'Marin, two bolt alloy',
    'Shifters': 'Shimano Deore, 10-speed',
    'Stem': 'Marin 3D forged alloy',
    'Tires': 'Schwalbe Hans Dampf, 27.5"x2.35"',
    'Wheelset': 'Marin Double Wall alloy'''
    }
BKESTREL_SPECS = {
    'Bottom Bracket': 'Praxis M30 BSA Bottom Bracket, '
                      'Cartridge Bearings',
    'Brakes': 'Tektro R540 dual-pivot',
    'Cassette': 'Shimano 105, 11-28T, 11-speed',
    'Chain': 'KMC X11, 11-speed',
    'Crankset': 'Oval Concepts 500, forged 6066 arms, M30 spindle, '
                'forged Praxis 50/34T rings',
    'Fork': 'EMH carbon, 1 1/8" - 1 1/4" tapered alloy steerer',
    'Frame': 'Kestrel Enhanced Modulus Hybrid (EMH) 700K & 800K '
             'carbon fiber',
    'Front Derailleur': 'Shimano 105, braze-on',
    'Grips/Tape': 'Kestrel padded',
    'Handlebar': 'Oval Concepts 310 Ergo, 6061 alloy, 31.8mm clamp, '
                 '133mm drop, 4° sweep',
    'Headset': 'FSA integrated, 1 1/8" top, 1 1/4" bottom w/ '
               '15mm top cover',
    'Levers': 'Shimano 105 STI',
    'Pedals': 'N/A',
    'Rear Derailleur': 'Shimano 105, 11-speed',
    'Rack Mounts': 'No',
    'Saddle': 'Oval Concepts 300, steel rail',
    'Seatpost': 'Kestrel EMS Pro, carbon, Ritchey clamp system',
    'Shifters': 'Shimano 105 STI, 11-speed',
    'Stem': 'Oval Concepts 313, 3D-forged 6061 stem body, +/-7°',
    'Tires': 'Vittoria Zaffiro Pro, 700 x 25c, folding',
    'Wheelset': 'Oval Concepts 327, 700c 20/24H rims'
}


class PerformanceBikesTestCase(unittest.TestCase):
    def setUp(self):
        # use smaller page_size for testing purposes
        self.pbs = PerformanceBikes(page_size=24)

    def test_fetch_prod_listing_view(self):
        text = self.pbs._fetch_prod_listing_view()
        soup = BeautifulSoup(text, 'lxml')
        self.pbs._get_prods_on_current_listings_page(soup)
        self.assertEqual(self.pbs._page_size, len(self.pbs._products))

    def test_get_bike_urls(self):
        # TODO - complete this unit test snippet (FYI - long running)
        response = self.pbs.get_all_available_prods()
        self.assertEqual(False, response)

    def test_get_max_num_products(self):
        # load test html into memory
        with open(SHOP_BIKES_HTML_PATH, encoding='utf-8') as f:
            prod_list_text = f.read()

        prod_list_soup = BeautifulSoup(prod_list_text, 'lxml')

        expected = 840  # from html file
        self.pbs._get_max_num_prods(prod_list_soup)
        self.assertEqual(expected, self.pbs._num_bikes)

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
        self.pbs._get_prods_on_current_listings_page(prod_list_soup)
        self.assertEqual(self.pbs._page_size, len(self.pbs._products))
        for key in cases:
            self.assertTrue(key in self.pbs._products)
        for value in cases.values():
            self.assertTrue(value in self.pbs._products.values())

    def test_get_prod_listings(self):
        self.pbs.get_all_available_prods(to_csv=False)
        self.assertTrue(self.pbs._num_bikes, len(self.pbs._products))

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(HTML_PATH, 'marin-hawk-hill-275-mountain-bike-2018-31-6715.html'))
        with open(html_path, encoding='utf-8') as f:            
            marin_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(HTML_PATH, 'bkestrel-talon-105-le-road-bike-2018-31-8721.html'))
        with open(html_path, encoding='utf-8') as f:
            bkestrel_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(HTML_PATH, 'bike-eli-elliptigo-sub-31-8914.html'))
        with open(html_path, encoding='utf-8') as f:
            generic_error = f.read()

        marin_detail_soup = BeautifulSoup(marin_prod_detail_text, 'lxml')
        bkestrel_detail_soup = BeautifulSoup(bkestrel_prod_detail_text,
                                                  'lxml')
        generic_error_soup = BeautifulSoup(generic_error, 'lxml')

        # case 1: exact match per example data
        result = self.pbs._parse_prod_specs(marin_detail_soup)
        self.assertEqual(len(MARIN_SPECS), len(result))
        for key in MARIN_SPECS.keys():
            self.assertEqual(MARIN_SPECS[key], result[key])

        # case 2: using second data, exact match in components
        result = self.pbs._parse_prod_specs(bkestrel_detail_soup)
        self.assertEqual(len(BKESTREL_SPECS), len(result))
        for key in BKESTREL_SPECS.keys():
            self.assertEqual(BKESTREL_SPECS[key], result[key])

        # case 3: safely handle error
        result = self.pbs._parse_prod_specs(generic_error_soup)
        self.assertEqual(0, len(result))

    def test_get_product_specs_scrape(self):
        """Long running unit test"""
        # case 1: attempt to get from memory when none available
        self.assertRaises(ValueError, self.pbs.get_product_specs,
                          get_prods_from='memory', to_csv=False)

        # case 2: scrape site to get available products but don't write to file
        result = self.pbs.get_product_specs(get_prods_from='site', to_csv=False)
        self.assertEqual(len(self.pbs._products), len(result))
        for key in self.pbs._products.keys():
            self.assertTrue(key in result.keys())

        # case 3: successfully get from memory now it is available
        result = self.pbs.get_product_specs(get_prods_from='memory',
                                            to_csv=False)
        self.assertEqual(len(self.pbs._products), len(result))
        for key in self.pbs._products.keys():
            self.assertTrue(key in result.keys())

    def test_get_product_specs_from_file(self):
        # case 1: invalid file path for using products from file
        self.assertRaises(TypeError, self.pbs.get_product_specs,
                          get_prods_from='dummy/file.txt', to_csv=False)

        # case 2: use products from file
        result = self.pbs.get_product_specs(get_prods_from=TEST_PROD_LISTING_PATH,
                                            to_csv=True)
        self.assertEqual(len(self.pbs._products), len(result))
        for key in self.pbs._products.keys():
            self.assertTrue(key in result.keys())

    def test_write_prod_listings_to_csv(self):
        # load test html into memory
        with open(SHOP_BIKES_HTML_PATH, encoding='utf-8') as f:
            prod_list_text = f.read()

        prod_list_soup = BeautifulSoup(prod_list_text, 'lxml')
        self.pbs._get_prods_on_current_listings_page(prod_list_soup)

        path = os.path.join(DATA_PATH,
                            f'test_performancebike_prod_listing_'
                            f'{TIMESTAMP}.csv')
        self.pbs._write_prod_listings_to_csv(path=path)

    def test_write_prod_specs_to_csv(self):
        test_specs_dict = {
            'marin_bike_spec': MARIN_SPECS,
            'bkestrel_bike_spec': BKESTREL_SPECS
        }
        fieldnames = [
            'Bottom Bracket', 'Brakes', 'Cassette', 'Chain',
            'Crankset', 'Fork', 'Frame', 'Front Derailleur',
            'Grips/Tape', 'Handlebar', 'Headset', 'Levers',
            'Pedals', 'Rear Derailleur', 'Rear Shock', 'Saddle', 'Seatpost',
            'Shifters', 'Stem', 'Tires', 'Wheelset', 'Rack Mounts'
        ]
        self.pbs._specs_fieldnames = set(fieldnames)

        path = os.path.join(DATA_PATH,
                            f'test_performancebike_prod_specs_'
                            f'{TIMESTAMP}.csv')
        self.pbs._write_prod_specs_to_csv(specs_dict=test_specs_dict,
                                          path=path)


if __name__ == '__main__':
    unittest.main()
