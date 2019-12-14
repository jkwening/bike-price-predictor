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
        self._scraper = NashBar(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = ['bmx_bikes', 'cyclocross_bikes',
                      'bike_forks_mountain_suspension',
                      'bike_frames', 'gravel_bikes',
                      'bike_hybrids_commuters_cruisers',
                      'kids_bikes_balance_bikes',
                      'mountain_bikes', 'road_bicycles',
                      'single_speed_fixed_gear_bikes']

        result = self._scraper._get_categories()
        print('\nCategories:', result)
        self.assertEqual(len(categories), len(result),
                         msg=f'Expected {len(categories)}; result {len(result)}')
        for key in categories:
            self.assertTrue(key in result,
                            msg=f'{key} is not in {result}!')

    def test_get_prods_listings(self):
        bike_type = 'road_bicycles'
        bike_cats = self._scraper._get_categories()
        endpoint = bike_cats[bike_type]['href']
        soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
            endpoint), 'lxml')

        # Verify product listings fetch
        self._scraper._get_prods_on_current_listings_page(soup, bike_type)
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 5,
                        msg=f'There are {num_prods} product first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        bike_type = 'road_bicycles'
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'nashbar_prods_all.csv')
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
                    'fork', 'cassette', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')


if __name__ == '__main__':
    unittest.main()
