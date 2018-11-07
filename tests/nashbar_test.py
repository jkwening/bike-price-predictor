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
CAVALO_SPECS = {
    'frame': 'C5 high-modulus carbon fiber, Tapered head tube, BB86 bottom bracket shell, Replaceable rear derailleur hanger',
    'fork': 'Full carbon fiber, 1-1/8" - 1-1/2" taper steerer',
    'headset': 'FSA NO.42 integrated, 1-1/8" upper - 1-1/2" lower',
    'crankset': 'Shimano Ultegra 6800, 52/36T chainrings, Crank arm length: 47cm=170mm, 50cm/53cm=172.5mm, 55cm/58cm=175mm',
    'bottom_bracket': 'Shimano SM-BB72-41B, BB86 Press Fit for road',
    'shifters': 'Shimano Ultegra 6800 shift/brake levers, 2x11-speed',
    'seatpost': 'Ritchey Comp alloy, 31.6mm x 300mm',
    'levers': 'Shimano Ultegra 6800',
    'front_derailleur': 'Shimano Ultegra 6800, Braze-on',
    'handlebar': 'Ritchey Comp Logic II alloy, 31.8mm diameter, 132mm drop, 78mm reach, Width: 47cm=40cm, 50cm/53cm=42cm, 55cm/58cm=44cm',
    'stem': 'Ritchey Comp 4-Axis alloy, 31.8mm clamp, 84/6-degree rise, Length: 47cm=90mm, 50cm/53cm=100mm, 55cm/58cm=120mm',
    'rear_derailleur': 'Shimano Ultegra 6800 SS, 11-speed',
    'cassette': 'Shimano 105 5800 11-speed, 11-28T',
    'brakes': 'Shimano Ultegra 6800',
    'wheelset': 'Shimano RS010 aluminum, 24mm rim height, 20 spokes front w/ radial lace pattern, 24 spokes rear w/ 2x lace pattern',
    'tires': 'Vittoria Zaffiro, 700x25, 26 TPI casing',
    'pedals': 'Not included',
    'saddle': 'Prologo K3 w/ steel rails',
    'chain': 'KMC X11',
    'grips/tape': 'Velo suede',
    'rack_mounts': 'None'
    }
FITWELL_SPECS = {
    'frame': 'FitWell double-butted seamless weld aluminum, replaceable derailleur hanger, English thread bottom bracket, clearance for 30mm width tires, 3 sets of water bottle braze-ons',
    'fork': 'A-Pro full carbon fiber, tapered 1-1/8" to 1.5" steerer tube',
    'headset': 'VP sealed cartridge IS for tapered',
    'crankset': 'Shimano R565, 50/34T compact chainrings',
    'bottom_bracket': 'Shimano 105 5700',
    'shifters': 'Shimano 105 5700, 2x10-speed',
    'seatpost': 'FitWell alloy, 27.2mm',
    'levers': 'Shimano 105 5700',
    'front_derailleur': 'Shimano 105 5700, 31.8mm clamp',
    'handlebar': 'FitWell alloy modern radius, 31.8mm diameter',
    'stem': 'FitWell 3D forged alloy, 31.8mm clamp',
    'rear_derailleur': 'Shimano 105 5700-GS 10-speed',
    'cassette': 'Shimano HG62 10-speed, 11-32T',
    'brakes': 'Shimano R561',
    'wheelset': 'Rims: Weinman DNZ18 aluminum, 23mm wide; Hubs: Novatec A171 aluminum, sealed cartridge, 24h (F), Novatec F172 aluminum, quad sealed cartridge, 28h (R); Spokes: 14g stainless steel',
    'tires': 'Maxxis Detonator, 700x28',
    'pedals': 'Not included',
    'saddle': 'FitWell road saddle, chromoly rails',
    'chain': 'Shimano Tiagra 4600',
    'grips/tape': 'Velo Vexgel, anti-slip',
    'rack_mounts': 'Yes'
}


class NashBarTestCase(unittest.TestCase):
    def setUp(self):
        # use smaller page_size for testing purposes
        self.pbs = NashBar(save_data_path=DATA_PATH, page_size=24)

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
        html_path = os.path.abspath(os.path.join(HTML_PATH, 'Cavalo-Carbon-Road Bike-Nashbar.html'))
        with open(html_path, encoding='utf-8') as f:            
            marin_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(HTML_PATH, 'FitWell-Road Bike-Nashbar.html'))
        with open(html_path, encoding='utf-8') as f:
            bkestrel_prod_detail_text = f.read()

        # TODO - replace with generic error page once I come across one
        # html_path = os.path.abspath(os.path.join(HTML_PATH, 'Nashbar-Carbon-Fork-Nashbar.html'))
        # with open(html_path, encoding='utf-8') as f:
        #     generic_error = f.read()

        marin_detail_soup = BeautifulSoup(marin_prod_detail_text, 'lxml')
        bkestrel_detail_soup = BeautifulSoup(bkestrel_prod_detail_text,
                                                  'lxml')
        # generic_error_soup = BeautifulSoup(generic_error, 'lxml')  # TODO

        # case 1: exact match per example data
        result = self.pbs._parse_prod_specs(marin_detail_soup)
        self.assertEqual(len(CAVALO_SPECS), len(result))
        for key in CAVALO_SPECS.keys():
            self.assertEqual(CAVALO_SPECS[key], result[key])

        # case 2: using second data, exact match in components
        result = self.pbs._parse_prod_specs(bkestrel_detail_soup)
        self.assertEqual(len(FITWELL_SPECS), len(result))
        for key in FITWELL_SPECS.keys():
            self.assertEqual(FITWELL_SPECS[key], result[key])

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

    def test_write_prod_listings_to_csv(self):
        # load test html into memory
        with open(SHOP_BIKES_HTML_PATH, encoding='utf-8') as f:
            prod_list_text = f.read()

        prod_list_soup = BeautifulSoup(prod_list_text, 'lxml')
        self.pbs._get_prods_on_current_listings_page(prod_list_soup)
        self.pbs._write_prod_listings_to_csv()

    def test_write_prod_specs_to_csv(self):
        test_specs_dict = {
            'marin_bike_spec': CAVALO_SPECS,
            'bkestrel_bike_spec': FITWELL_SPECS
            }
        fieldnames = [
            'bottom_bracket', 'brakes', 'cassette', 'chain',
            'crankset', 'fork', 'frame', 'front_derailleur',
            'grips/tape', 'handlebar', 'headset', 'levers',
            'pedals', 'rear_derailleur', 'rear_shock', 'saddle', 'seatpost',
            'shifters', 'stem', 'tires', 'wheelset', 'rack_mounts'
        ]
        self.pbs._specs_fieldnames = set(fieldnames)
        self.pbs._write_prod_specs_to_csv(specs_dict=test_specs_dict)


if __name__ == '__main__':
    unittest.main()
