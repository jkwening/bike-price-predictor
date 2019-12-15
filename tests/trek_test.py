# python modules
import unittest
import os
from datetime import datetime

from bs4 import BeautifulSoup

# package modules
from scrapers.trek import Trek

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
SHOP_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'trek-bikes.html'))
SAMPLE_SPECS1 = {'frame': 'High-performance hydroformed e-bike frame w/integrated battery and Motor Armor', 'fork': 'Rigid carbon w/15mm thru axle', 'front_hub': 'Bontrager sealed bearing, 15mm alloy axle', 'rear_hub': 'Bontrager sealed cartridge bearing rear hub', 'rims': 'Alex Volar alloy, 27.5˝, 32h', 'tires': 'Schwalbe Super Moto-X w/GreenGuard puncture protection, 650Bx2.40', 'shifters': 'Shimano Deore M6000, 10 speed', 'rear_derailleur': 'Shimano Deore M6000, shadow Plus', 'crank': 'Miranda Delta, 18T w/chainguard', 'cassette': 'Shimano HG500, 11-42, 10-speed', 'chain': 'KMC X10E', 'pedals': 'Wellgo track-style alloy', 'saddle': 'Bontrager H1', 'seatpost': 'Bontrager alloy, 2-bolt head, 31.6mm, 8mm offset', 'handlebar': 'Bontrager alloy, 31.8mm, 15mm rise', 'grips': 'Bontrager Satellite Elite, lock-on, ergonomic', 'stem': 'Bontrager Elite Blendr, w/mount for Supernova light', 'headset': 'Integrated, cartridge bearing, sealed, 1-1/8˝ top, 1.5˝ bottom', 'brakeset': 'Shimano M315, hydraulic disc', 'battery': 'Bosch PowerPack 500Wh, integrated in frame', 'controller': 'Bosch Purion', 'motor': 'Bosch Performance Line, 250 watt, 63Nm, 20 mph', 'front_light': 'Supernova Mini 2, 205 lumen w/daytime running light', 'rear_light': 'Supernova E3 rear light, LED', 'extras': '2A Bosch Charger', 'weight_limit': 'This bike has a maximum total weight limit (combined weight of bicycle, rider, and cargo) of 300 pounds (136 kg).'}
SAMPLE_SPECS2 = {'frame': '600 Series OCLV Carbon, Front IsoSpeed, Adjustable Rear IsoSpeed, tapered head tube, BB90, flat mount disc brakes, 12mm thru-axle, internal cable routing, hidden fender mounts, 3S chain keeper, DuoTrap S compatible, Ride Tuned seatmast', 'fork': 'Domane full carbon disc, carbon tapered steerer, flat mount disc brakes, 12mm thru-axle', 'wheels': 'Bontrager Paradigm Comp Tubeless Ready Disc, 12mm thru axle', 'tires': 'Bontrager R3 Hard-Case Lite, 120 tpi, aramid bead, 700x32c', 'max_tire_size': '32c Bontrager tires (with at least 4mm of clearance to frame)', 'shifters': 'Shimano Ultegra, 11 speed', 'front_derailleur': 'Shimano Ultegra, braze-on', 'rear_derailleur': 'Shimano Ultegra, 11 speed', 'crank': 'Shimano Ultegra, 50/34 (compact)', 'bottom_bracket': 'BB90', 'cassette': 'Shimano Ultegra, 11-32, 11 speed', 'chain': 'Shimano Ultegra', 'pedals': 'Not included', 'saddle': 'Bontrager Arvada Elite, stainless rails', 'seatpost': 'Bontrager Ride Tuned carbon seatmast cap, 20mm offset', 'handlebar': 'Bontrager Pro IsoCore VR-CF, 31.8mm', 'grips': 'Bontrager tape', 'stem': 'Bontrager Pro, 31.8mm, 7 degree, w/computer & light mounts', 'headset': 'Integrated, cartridge bearing, sealed, 1-1/8˝ top, 1.5˝ bottom', 'brakeset': 'Shimano Ultegra flat mount hydraulic disc', 'weight': '56cm - 8.11 kg / 17.88 lbs', 'weight_limit': 'This bike has a maximum total weight limit (combined weight of bicycle, rider, and cargo) of 275 pounds (125 kg).'}
SAMPLE_SPECS3 = {'frame': 'Alpha Platinum Aluminum, ABP, Boost148, Knock Block steerer stop, Full Floater, EVO link, tapered head tube, Mino Link, Control Freak internal routing, down tube guard, PF92, ISCG 05, G2 Geometry, 130mm travel', 'front_suspension': 'Fox Rhythm 34 Float, GRIP adjustable damper, tapered steerer, G2 Geometry w/51mm offset, Boost110, 130mm travel', 'rear_suspension': 'Fox Performance Float EVOL, RE:aktiv 3-position damper, tuned by Trek Suspension Lab, 210x52.5mm', 'wheels': 'Bontrager Line Comp 30, Tubeless Ready, 54T Rapid Drive, Boost110 front, Boost148 rear, tubeless strips included, valves sold separately', 'tires': 'Bontrager XR4 Team Issue, Tubeless Ready, Inner Strength sidewalls, 120tpi, aramid bead, 29x2.40˝', 'shifters': 'SRAM GX Eagle, 12 speed', 'rear_derailleur': 'SRAM GX Eagle, Roller Bearing Clutch', 'crank': 'Truvativ Descendant 6k Eagle DUB, 32T Direct Mount', 'bottom_bracket': 'SRAM DUB Press Fit, 92mm', 'cassette': 'SRAM XG-1275 Eagle, 10-50, 12 speed', 'chain': 'SRAM GX Eagle', 'pedals': 'Not included', 'saddle': 'Bontrager Arvada, hollow chromoly rails', 'seatpost': 'Bontrager Line, internal routing, 31.6mm, 15.5: 100mm, 17.5 & 18.5: 125mm, 19.5 & 21.5: 150mm', 'handlebar': 'Bontrager Line, 35mm, 15mm rise, 750mm width', 'grips': 'Bontrager XR Trail Elite, alloy lock-on', 'stem': 'Bontrager Line, Knock Block, 35mm clamp, 0 degree', 'headset': 'Knock Block Integrated, sealed cartridge bearing, 1-1/8˝ top, 1.5˝ bottom', 'brakeset': 'Shimano Deore M6000 hydraulic disc', 'weight': '17.5˝ - 13.79 kg / 30.4 lbs (with tubes)', 'weight_limit': 'This bike has a maximum total weight limit (combined weight of bicycle, rider, and cargo) of 300 pounds (136 kg).'}


class SpecializedTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Trek(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = [
            'road',
            'mountain',
            'fitness',
            'electric',
            'kids',
            'cyclocross',
            'gravel',
            'womens',
            'cross_country',
            'downhill'
        ]

        result = self._scraper._get_categories()
        print('\nCategories:', result)
        for key in categories:
            self.assertTrue(key in result,
                            msg=f'{key} is not in {result}!')

    def test_get_prods_listings(self):
        bike_type = 'road'
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
        bike_type = 'road'
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'trek_prods_all.csv')
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
