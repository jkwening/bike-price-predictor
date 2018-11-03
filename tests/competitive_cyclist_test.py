# python modules
import unittest
import os
from bs4 import BeautifulSoup
from datetime import datetime

# package modules
from scrapers.competitive_cyclist import CompetitiveCyclist

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
TEST_PROD_LISTING_PATH = os.path.join(TEST_DATA_PATH, 'performance_prod_listing_test_data.csv')
SHOP_BIKES_HTML_PATH = os.path.abspath(os.path.join(HTML_PATH, 'Competitive-Cyclist.html'))
PINARELLO_SPECS = {
    'Frame Material': 'Toray T1100 1K Dream Carbon Fiber',
    'Fork': 'Onda',
    'Fork Material': 'Toray T1100 1K Dream Carbon Fiber',
    'Headset': '1-1/8 - 1-1/2 in',
    'Shifters': 'SRAM Red eTap',
    'Front Derailleur': 'SRAM Red eTap',
    'Rear Derailleur': 'SRAM Red eTap',
    'Crankset': '53 / 39 t SRAM Red GXP, 52 / 36 t SRAM Red GXP, 50 / 34 t SRAM Red GXP',
    'Bottom Bracket': '[shell] Italian threaded, [adapter] SRAM GXP Team',
    'Crank Arm Length': '170 mm, 172.5 mm, 175 mm',
    'Cassette': '11 - 25 t SRAM XG-1190',
    'Chain': 'SRAM PC-Red',
    'Brakeset': 'SRAM Red Aero Link',
    'Brake Type': 'rim',
    'Handlebar': 'Zipp SL-70 Aero Carbon',
    'Handlebar Width': '[42cm, 44cm, 46.5cm] 38 cm, [50cm, 51.5cm] 40 cm, [sizes 53cm, 54cm] 42 cm, [sizes 55cm, 56cm, 57.5cm, 59.5cm, 62cm] 44 cm',
    'Bar Tape': 'Arundel cork',
    'Stem': 'Zipp SL Sprint Carbon',
    'Saddle': 'Fizik Aliante R7',
    'Seatpost': 'Dogma Aero',
    'Seat Collar': 'TwinForce (integrated)',
    'Wheelset': 'Zipp 404 NSW Carbon Clincher',
    'Hubs': 'Zipp Cognition',
    'Skewers': '9mm quick-release',
    'Tires': 'Vittoria Corsa G Plus',
    'Tire Size': '700 c x 25 mm',
    'Pedals': 'not included',
    'Recommended Use': 'cycling',
    'Manufacturer Warranty': '2 years on frame'
    }
RIDLEY_SPECS = {
    'Frame Material': '30t and 24t high-modulus carbon fiber',
    'Fork': 'Oryx Disc 12TA, carbon steerer',
    'Fork Material': 'carbon fiber',
    'Shifters': 'Shimano ST-R685',
    'Front Derailleur': 'Shimano Ultegra 6800',
    'Rear Derailleur': 'Shimano Ultegra 6800',
    'Crankset': '46 / 36 t Shimano Ultegra 6800',
    'Bottom Bracket': 'PF30',
    'Cassette': '11 - 28 t Shimano 105 5800',
    'Chain': 'KMC X11',
    'Brakeset': 'Shimano BR-RS805/BR-RS785 Hydraulic',
    'Rotors': '[front] 60 mm, [rear] 140 mm',
    'Handlebar': '4ZA Cirrus E.2',
    'Stem': '4ZA Cirrus',
    'Saddle': '4ZA Cirrus Pro Cr/Ti rails',
    'Seatpost': '4ZA Cirrus Carbon 27.2 x 350mm',
    'Wheelset': 'DT Swiss R23 Spline DB',
    'Front Axle': '12TA',
    'Tires': 'Clement MXP Tubeless Ready',
    'Tire Size': '700 c x 33 mm',
    'Pedals': 'not included',
    'Recommended Use': 'cyclocross',
    'Manufacturer Warranty': '5 years on frame'
}


class CompetitiveCyclistTestCase(unittest.TestCase):
    def setUp(self):
        # use smaller page_size for testing purposes
        self._cc = CompetitiveCyclist(save_data_path=DATA_PATH)

    def test_fetch_prod_listing_view(self):
        text = self._cc._fetch_prod_listing_view()
        soup = BeautifulSoup(text, 'lxml')
        self._cc._get_prods_on_current_listings_page(soup)
        self.assertEqual(42, len(self._cc._products))

    def test_get_bike_urls(self):
        # TODO - complete this unit test snippet (FYI - long running)
        response = self._cc.get_all_available_prods()
        self.assertEqual(False, response)

    def test_get_num_pages(self):
        # load test html into memory
        with open(SHOP_BIKES_HTML_PATH, encoding='utf-8') as f:
            prod_list_text = f.read()

        prod_list_soup = BeautifulSoup(prod_list_text, 'lxml')

        expected = 3  # from html file
        result = self._cc._get_num_pages(prod_list_soup)
        self.assertEqual(expected, result)

    # TODO: finish this unit test logic has preformance data not competitive
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
        self._cc._get_prods_on_current_listings_page(prod_list_soup)
        self.assertEqual(self._cc._page_size, len(self._cc._products))
        for key in cases:
            self.assertTrue(key in self._cc._products)
        for value in cases.values():
            self.assertTrue(value in self._cc._products.values())

    def test_get_prod_listings(self):
        self._cc.get_all_available_prods(bike_type_list=['road'], to_csv=False)
        self.assertTrue(self._cc._num_bikes, len(self._cc._products))

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
        result = self._cc._parse_prod_specs(marin_detail_soup)
        self.assertEqual(len(PINARELLO_SPECS), len(result))
        for key in PINARELLO_SPECS.keys():
            self.assertEqual(PINARELLO_SPECS[key], result[key])

        # case 2: using second data, exact match in components
        result = self._cc._parse_prod_specs(bkestrel_detail_soup)
        self.assertEqual(len(RIDLEY_SPECS), len(result))
        for key in RIDLEY_SPECS.keys():
            self.assertEqual(RIDLEY_SPECS[key], result[key])

        # case 3: safely handle error
        result = self._cc._parse_prod_specs(generic_error_soup)
        self.assertEqual(0, len(result))

    def test_get_product_specs_scrape(self):
        """Long running unit test"""
        # case 1: attempt to get from memory when none available
        self.assertRaises(ValueError, self._cc.get_product_specs,
                          get_prods_from='memory', to_csv=False)

        # case 2: scrape site to get available products but don't write to file
        result = self._cc.get_product_specs(get_prods_from='site', to_csv=False)
        self.assertEqual(len(self._cc._products), len(result))
        for key in self._cc._products.keys():
            self.assertTrue(key in result.keys())

        # case 3: successfully get from memory now it is available
        result = self._cc.get_product_specs(get_prods_from='memory',
                                            to_csv=False)
        self.assertEqual(len(self._cc._products), len(result))
        for key in self._cc._products.keys():
            self.assertTrue(key in result.keys())

    def test_get_product_specs_from_file(self):
        # case 1: invalid file path for using products from file
        self.assertRaises(TypeError, self._cc.get_product_specs,
                          get_prods_from='dummy/file.txt', to_csv=False)

        # case 2: use products from file
        result = self._cc.get_product_specs(get_prods_from=TEST_PROD_LISTING_PATH,
                                            to_csv=True)
        self.assertEqual(len(self._cc._products), len(result))
        for key in self._cc._products.keys():
            self.assertTrue(key in result.keys())

    def test_write_prod_listings_to_csv(self):
        # load test html into memory
        with open(SHOP_BIKES_HTML_PATH, encoding='utf-8') as f:
            prod_list_text = f.read()

        prod_list_soup = BeautifulSoup(prod_list_text, 'lxml')
        self._cc._get_prods_on_current_listings_page(prod_list_soup)

        path = os.path.join(DATA_PATH,
                            f'test_performancebike_prod_listing_{TIMESTAMP}.csv')
        self._cc._write_prod_listings_to_csv(path=path)

    def test_write_prod_specs_to_csv(self):
        test_specs_dict = {
            'marin_bike_spec': PINARELLO_SPECS,
            'bkestrel_bike_spec': RIDLEY_SPECS
        }
        fieldnames = [
            'Bottom Bracket', 'Brakes', 'Cassette', 'Chain',
            'Crankset', 'Fork', 'Frame', 'Front Derailleur',
            'Grips/Tape', 'Handlebar', 'Headset', 'Levers',
            'Pedals', 'Rear Derailleur', 'Rear Shock', 'Saddle', 'Seatpost',
            'Shifters', 'Stem', 'Tires', 'Wheelset', 'Rack Mounts'
        ]
        self._cc._specs_fieldnames = set(fieldnames)

        path = os.path.join(DATA_PATH,
                            f'test_performancebike_prod_specs_{TIMESTAMP}.csv')
        self._cc._write_prod_specs_to_csv(specs_dict=test_specs_dict,
                                          path=path)


if __name__ == '__main__':
    unittest.main()
