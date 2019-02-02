# python modules
import unittest
import os
from datetime import datetime

from bs4 import BeautifulSoup

# package modules
from scrapers.eriks import EriksBikes

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
SHOP_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'eriks-guide.html'))
ROAD_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'eriks-road.html')
)
STRIDER_SPECS = {
    'frame': '6061 Aluminum Floval Tubing, Easy Standover',
    'fork': 'Micro Landing Gear',
    'wheels': '16H Alloy Hubs, Alloy Rims',
    'tires': '12" x 2.125" Front & Rear',
    'headset': '1-1/8" Threadless',
    'stem': 'Top-Load Alloy, 40mm Reach',
    'handlebars': '16" x 2" Alloy',
    'grips': 'Mini Kraton',
    'saddle': 'SE Racing Mini Seat / Post Combo',
    'seat_post': 'Integrated Alloy, 22.2mm',
    'seat_binder': 'Alloy Quick Release, 31.8mm Inner Diameter'
}
BIANCHI_SPECS = {
    'frame': 'Intenso Disc carbon',
    'fork': 'Bianchi Full Carbon w/Kevlar Disc',
    'shifters': 'Shimano Ultegra ST-R8020 2x11sp',
    'front_derailleur': 'Shimano Ultegra FD-R8000',
    'rear_derailleur': 'Shimano Ultegra RD-R8000 GS 11sp',
    'brakes': 'Shimano BR-R8070',
    'brake_levers': 'included w/shifters',
    'cranks': 'Shimano Ultegra FC-R8000 50x34T',
    'cassette': 'Shimano Ultegra CS-R8000, 11-30T',
    'bottom_bracket': 'Shimano SM-BBR60',
    'chain': 'Shimano Ultegra CN-HG701-11, 11sp',
    'rims': 'Fulcrum Racing 618 disc brake',
    'tires': 'Vittoria Zaffiro Pro Slick 700x25',
    'headset': 'Fsa Orbit C-40-ACB',
    'stem': 'Reparto Corse Alloy 6061',
    'handlebars': 'Reparto Corse Compact, alloy 6061',
    'grips': 'La Spirale Ribbon cork',
    'saddle': 'Selle Royal SR Asphalt GF',
    'seat_post': 'Reparto Corse Alloy 2014'
}
RUBY_SPECS = {
    'frame': 'Specialized FACT 9r carbon, Women\'s Endurance Geometry, '
             'Rider-First Engineered, 12x142mm thru-axle, Future Shock suspension, 20mm of travel, flat disc mounts',
    'fork': 'Specialized FACT full-carbon, flat-mount disc, 12x100mm thru-axle',
    'shifters': 'Shimano Tiagra',
    'front_derailleur': 'Shimano Tiagra, braze-on',
    'rear_derailleur': 'Shimano Tiagra, long cage, 10-speed',
    'brakes': 'Tektro Spyre, flat mount, mechanical disc',
    'cranks': 'Shimano Tiagra 50/34T',
    'cassette': 'Shimano Tiagra, 10-speed, 11-34t',
    'chain': 'KMC X10EL, 10-speed w/ Missing Link',
    'wheels': 'Axis Sport Disc',
    'tires': 'Espoir Sport, 60 TPI, wire bead, double BlackBelt protection, 700x28mm',
    'stem': 'Specialized, 3D forged alloy, 4-bolt, 7-degree rise',
    'handlebars': 'Specialized Shallow Drop, 6061, 70x125mm, 31.8mm clamp',
    'grips': 'Specialized S-Wrap',
    'saddle': 'Women\'s Body Geometry Myth Sport thin, Steel rails, 155mm',
    'seat_post': 'Specialized, alloy, single bolt, 27.2mm'
}

class EriksBikesTestCase(unittest.TestCase):
    def setUp(self):
        self._eriks = EriksBikes(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = [
            'road_bikes',
            'mountain_bikes',
            'path_pavement_bikes',
            'electric_bikes',
            'youth_bikes',
            'bmx_bikes'
        ]

        with open(SHOP_BIKES_HTML_PATH, mode='r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        result = self._eriks._get_categories(soup)
        print('categories:', result)
        for key in result:
            self.assertTrue(key in categories,
                            msg=f'{key} is not in categories!')

    def test_get_prod_listings(self):
        with open(ROAD_BIKES_HTML_PATH, mode='r',
                  encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'lxml')
        num_bikes = self._eriks._get_prods_on_current_listings_page(
            soup, 'road_bikes', get_num_bikes=True)
        self.assertEqual(30, len(self._eriks._products),
                         msg='First page should return 30 products.')
        self.assertTrue(239, num_bikes)

    def test_get_all_available_prods(self):
        # Scrape each bike_type first page and get total num bikes
        total_bikes = 0
        for bike_type in self._eriks._BIKE_CATEGORIES.keys():
            endpoint = self._eriks._BIKE_CATEGORIES[bike_type]['href']

            # Scrape first page, get num bikes, and determine num pages
            soup = BeautifulSoup(self._eriks._fetch_prod_listing_view(
                endpoint, page=1), 'lxml')
            num_bikes = self._eriks._get_prods_on_current_listings_page(
                soup, bike_type, get_num_bikes=True
            )
            total_bikes += num_bikes
        print(f'Expecting {total_bikes} total bikes.')

        # Validate method
        self._eriks.get_all_available_prods()
        num_prods = len(self._eriks._products)
        # There are dupes so expect less num_prods
        self.assertTrue(total_bikes >= num_prods,
                        msg=f'expected: {total_bikes} - found: {num_prods}')

    def test_parse_prod_spec(self):
        # load test prod details into memory
        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'eriks-Bianchi-Road-Bikes.html'))
        with open(html_path, encoding='utf-8') as f:
            bianchi_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'eriks-ripper.html'))
        with open(html_path, encoding='utf-8') as f:
            strider_prod_detail_text = f.read()

        html_path = os.path.abspath(os.path.join(
            HTML_PATH, 'eriks-ruby.html'))
        with open(html_path, encoding='utf-8') as f:
            ruby_prod_detail_text = f.read()

        # html_path = os.path.abspath(os.path.join(
        #     HTML_PATH, 'conte-Specialized-Boys-Hotwalk.html'))
        # with open(html_path, encoding='utf-8') as f:
        #     generic_error = f.read()

        bianchi_detail_soup = BeautifulSoup(
            bianchi_prod_detail_text, 'lxml')
        strider_detail_soup = BeautifulSoup(
            strider_prod_detail_text, 'lxml')
        ruby_detail_soup = BeautifulSoup(
            ruby_prod_detail_text, 'lxml'
        )
        # generic_error_soup = BeautifulSoup(generic_error, 'lxml')

        # case 1: exact match per example data
        result = self._eriks._parse_prod_specs(bianchi_detail_soup)
        self.assertEqual(len(BIANCHI_SPECS), len(result))
        for key in BIANCHI_SPECS.keys():
            self.assertEqual(
                BIANCHI_SPECS[key], result[key])

        # case 2: using second data, exact match in components
        result = self._eriks._parse_prod_specs(strider_detail_soup)
        self.assertEqual(len(STRIDER_SPECS), len(result))
        for key in STRIDER_SPECS.keys():
            self.assertEqual(STRIDER_SPECS[key], result[key])

        # case 3: using third data, exact match in components
        result = self._eriks._parse_prod_specs(ruby_detail_soup)
        self.assertEqual(len(RUBY_SPECS), len(result))
        for key in RUBY_SPECS.keys():
            self.assertEqual(RUBY_SPECS[key], result[key],
                             msg=f'{key}: Expected - {RUBY_SPECS[key]}; '
                             f'Result - {result[key]}')

        # # case 4: safely handle missing specs
        # result = self._eriks._parse_prod_specs(generic_error_soup)
        # self.assertEqual(0, len(result))


if __name__ == '__main__':
    unittest.main()
