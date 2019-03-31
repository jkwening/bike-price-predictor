# python modules
import unittest
import os
from bs4 import BeautifulSoup
from datetime import datetime

# package modules
from scrapers.nashbar import NashBar

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
TEST_PROD_LISTING_PATH = os.path.join(TEST_DATA_PATH, 'nashbar_prod_listing_test_data.csv')
SHOP_BIKES_HTML_PATH = os.path.abspath(os.path.join(HTML_PATH, 'nashbar.html'))
RITCHEY_SPECS = {'frame': 'Ritchey SwissCross Disc',
                'fork': 'Ritchey Cross WCS Carbon',
                'headset': 'Ritchey WCS Drop In 1-1/8"',
                'rear_derailleur': 'Shimano Ultegra 11s',
                'front_derailleur': 'Shimano Ultegra 2s',
                'shifters': 'Shimano RS685 Hydraulic Disc',
                'brakes': 'Shimano RS785 Hydraulic Disc',
                'rotors': 'Shimano RT99-S 160mm',
                'crankset': 'Shimano Ultegra 50/34 \x96 170mm (49/51cm),172.5mm (53/55cm), 175mm (57/59cm)',
                'bb_set': 'Shimano Ultegra BBR60 (BSA)',
                'handlebar': 'Ritchey EvoMax WCS Blatte \x96 42cm (49/51cm), 44cm (53/55cm), 46cm (57/59cm)',
                'bar_tape': 'Ritchey Cork Black',
                'stem': 'Ritchey C-220 WCS Blatte \x96 80mm (49/51cm), 90mm (53cm), 100mm (55cm), 110mm (57/59cm)',
                'seatpost': 'Ritchey Link WCS 350x27.2mm Blatte',
                'saddle': 'Ritchey Streem WCS Black',
                'wheelset': 'Ritchey Zeta Disc WCS',
                'chain': 'Shimano Ultegra HG700 11s',
                'cassette': 'Shimano CS-5800 11s 11/28T',
                'tires': 'Ritchey Shield 700x35 Comp foldable',
                'color': 'Black'
                }
FUJI_SPECS = {
    'sizes': 'XS (13"), S (15"),',
    'color': 'Light Orange',
    'frame': 'Fuji A1-SL alloy front and rear triangle, cold-forged dropout and replaceable hanger',
    'fork': 'Zoom CH-565 w/ 60mm travel',
    'crankset': 'Prowheel, alloy, 48/38/28T w/ chainguard',
    'bottom_bracket': 'Semi-cartridge bearing',
    'pedals': 'Resin platform',
    'front_derailleur': 'Shimano Tourney, 31.8mm',
    'rear_derailleur': 'Shimano Tourney, 7-speed',
    'shifters': 'Shimano EF41, EZ Fire, 7-speed',
    'cassette': 'Shimano freewheel, 14-28T, 7-speed',
    'chain': 'KMC Z50, 7-speed',
    'wheelset': 'Fuji Aluminum rims, Formula DC-20 front, DC-31 rear disc hub, 14g black spokes',
    'tires': 'Vera Eos, 27.5" x 2.1", 30tpi',
    'brakeset': 'Tektro M-280, mechanical disc, 160mm rotors',
    'brake_levers': 'Shimano EF41, 2-finger brake/shifter combo',
    'headset': '1 1/8", caged bearings',
    'handlebar': 'Steel riser bar, 25.4mm, 6 sweep, 30mm rise',
    'stem': 'Steel, +/-25°',
    'grips': 'Single density Kraton',
    'saddle': 'Padded MTB, steel rail',
    'seatpost': 'Alloy, 27.2mm'
}


class NashBarTestCase(unittest.TestCase):
    def setUp(self):
        # use smaller page_size for testing purposes
        self.pbs = NashBar(save_data_path=DATA_PATH, page_size=24)

    def test_get_categories(self):
        categories = ['bmx_bikes', 'cyclocross_bikes',
                      'bike_forks_mountain_suspension',
                      'bike_frame_protection', 'bike_frames', 'gravel_bikes',
                      'bike_hybrids_commuters_cruisers',
                      'kids_bikes_balance_bikes',
                      'mountain_bikes', 'road_bicycles',
                      'single_speed_fixed_gear_bikes']
        self.assertEqual(len(categories), len(self.pbs._BIKE_CATEGORIES),
                         msg=f'Expected: {len(categories)}; Actual: {len(self.pbs._BIKE_CATEGORIES)}')
        for r in self.pbs._BIKE_CATEGORIES:
            self.assertTrue(r in categories,
                            msg=f'{r} not in {categories}')

    def test_fetch_prod_listing_view(self):
        text = self.pbs._fetch_prod_listing_view()
        soup = BeautifulSoup(text, 'lxml')
        self.pbs._get_prods_on_current_listings_page(soup)
        self.assertEqual(self.pbs._page_size, len(self.pbs._products))

    def test_get_max_num_products(self):
        # load test html into memory
        with open(SHOP_BIKES_HTML_PATH, encoding='utf-8') as f:
            prod_list_text = f.read()

        prod_list_soup = BeautifulSoup(prod_list_text, 'lxml')

        expected = 467  # from html file
        self.pbs._get_max_num_prods(prod_list_soup)
        self.assertEqual(expected, self.pbs._num_bikes)

    def test_get_prods_on_page(self):
        cases = {
            '511632':  {'href': '/cycling/bikes-frames/nashbar-carbon-road-bike-fork-ns-icrf-base', 'desc': 'Nashbar Carbon Road Bike Fork', 'price': '$89.99', 'msrp': '$159.99', 'id': '511632'},
            '1024819115206121167174928':  {'href': '/cycling/bikes-frames/nashbar-rigid-26-quot%3B-mountain-bike-fork-ns-cmf-base', 'desc': 'Nashbar Rigid 26" Mountain Bike Fork', 'price': '$49.99', 'msrp': '$84.99', 'id': '1024819115206121167174928'},
            '1024819115206121167592693':  {'href': '/cycling/bikes-frames/lizard-skins-large-neoprene-chainstay-protector-ls-ncpl', 'desc': 'Lizard Skins Large Neoprene Chainstay Protector', 'price': '$10.99', 'msrp': '$10.99', 'id': '1024819115206121167592693'},
            '1024819115206121167602766':  {'href': '/cycling/bikes-frames/fuji-captiva-comfort-bike-closeout-yb-cap-base', 'desc': 'Fuji Captiva Comfort Bike - Closeout', 'price': '$249.99', 'msrp': '$349.99', 'id': '1024819115206121167602766'},
            '1024819115206121167593619':  {'href': '/cycling/bikes-frames/nashbar-derailleur-hanger-3-nb-dh3-base', 'desc': 'Nashbar Derailleur Hanger 3', 'price': '$7.99', 'msrp': '$15.00', 'id': '1024819115206121167593619'},
            '1024819115206121167602976':  {'href': '/cycling/bikes-frames/cavalo-carbon-ultegra-road-bike-cv-ultc', 'desc': 'Cavalo Carbon Ultegra Road Bike', 'price': '$1,399.99', 'msrp': '$3,999.99', 'id': '1024819115206121167602976'},
            '1024819115206121167603120':  {'href': '/cycling/bikes-frames/lizard-skins-fork-protector-clear-ls-fkpc-base', 'desc': 'Lizard Skins Fork Protector - Clear', 'price': '$24.99', 'msrp': '$24.99', 'id': '1024819115206121167603120'},
            '1024819115206121167174979':  {'href': '/cycling/bikes-frames/nashbar-carbon-road-bike-fork-ns-crf', 'desc': 'Nashbar Carbon Road Bike Fork', 'price': '$99.99', 'msrp': '$169.99', 'id': '1024819115206121167174979'}
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
        self.pbs.get_all_available_prods(to_csv=True)
        self.assertTrue(self.pbs._num_bikes, len(self.pbs._products))

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(HTML_PATH, 'Ritchey-Performance Bike.html'))
        with open(html_path, encoding='ISO-8859-1') as f:
            ritchey_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(HTML_PATH, 'Fuji-Performance Bike.html'))
        with open(html_path, encoding='ISO-8859-1') as f:
            fuji_prod_detail_text = f.read()

        # TODO - replace with generic error page once I come across one
        # html_path = os.path.abspath(os.path.join(HTML_PATH, 'Nashbar-Carbon-Fork-Nashbar.html'))
        # with open(html_path, encoding='utf-8') as f:
        #     generic_error = f.read()

        ritchey_detail_soup = BeautifulSoup(ritchey_prod_detail_text, 'lxml')
        fuji_detail_soup = BeautifulSoup(fuji_prod_detail_text,
                                                  'lxml')
        # generic_error_soup = BeautifulSoup(generic_error, 'lxml')  # TODO

        # case 1: exact match per example data
        result = self.pbs._parse_prod_specs(ritchey_detail_soup)
        self.assertEqual(len(RITCHEY_SPECS), len(result))
        for key in RITCHEY_SPECS.keys():
            self.assertEqual(RITCHEY_SPECS[key], result[key])

        # case 2: using second data, exact match in components
        result = self.pbs._parse_prod_specs(fuji_detail_soup)
        self.assertEqual(len(FUJI_SPECS), len(result))
        for key in FUJI_SPECS.keys():
            self.assertEqual(FUJI_SPECS[key], result[key])

        # TODO case 3: safely handle error
        # result = self.pbs._parse_prod_specs(generic_error_soup)
        # self.assertEqual(0, len(result))

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


if __name__ == '__main__':
    unittest.main()
