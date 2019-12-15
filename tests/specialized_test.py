# python modules
import unittest
import os
from datetime import datetime

from bs4 import BeautifulSoup

# package modules
from scrapers.specialized import Specialized

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
SHOP_BIKES_HTML_PATH = os.path.abspath(
    os.path.join(HTML_PATH, 'specialized-mountain-bikes.html'))
ALLEZ_SPECS = {
    'bottom_bracket': 'BSA, 68mm, square-taper',
    'chain': 'KMC X8 w/ Missing Link™, 8-speed',
    'crankset': 'Shimano Claris R200',
    'shift_levers': 'Shimano Claris 2000, 8-speed',
    'front_derailleur': 'Shimano Claris, clamp-on',
    'cassette': 'SunRace, 8-speed, 11-32t',
    'chainrings': '50/34T',
    'rear_derailleur': 'Shimano Claris, 8-speed',
    'fork': 'Specialized FACT carbon, 1-1/8" to 1-3/8" taper, fender eyelets',
    'saddle': 'Body Geometry Toupé Sport, steel rails, 143mm',
    'seat_binder': 'Bolt-type, 31.8mm',
    'tape': 'Specialized S-Wrap',
    'seatpost': 'Alloy, 2-bolt Clamp, 12mm offset, 27.2mm, anti-corrosion hardware',
    'handlebars': 'Specialized Shallow Drop, 6061, 70x125mm, 31.8mm clamp',
    'stem': 'Specialized, 3D-forged alloy, 4-bolt, 6-degree rise',
    'rear_wheel': 'Axis Sport',
    'inner_tubes': 'Presta, 40mm valve',
    'front_tire': 'Espoir Sport, 60 TPI, wire bead, double BlackBelt protection, 700x25mm',
    'rear_tire': 'Espoir Sport, 60 TPI, wire bead, double BlackBelt protection, 700x25mm',
    'front_wheel': 'Axis Sport',
    'front_brake': 'Tektro, alloy, dual-pivot',
    'rear_brake': 'Tektro, alloy, dual-pivot',
    'pedals': 'Nylon, 105x78x28mm, loose ball w/ reflectors',
    'frame': 'Specialized E5 Premium Aluminum, fully manipulated tubing w/ SmoothWelds, 1-1/8"- 1-3/8" tapered head tube, internal cable routing, threaded BB, 130mm spacing'
}
COMO_SPECS = {
    'chain': 'Shimano E6070, 9-speed',
    'shift_levers': 'Shimano Alivio, 9-speed w/ Optical Gear Display',
    'cassette': 'Shimano CS-HG200, 9-speed, 11-36t',
    'chainrings': '40T, 104 BCD w/ chainguard',
    'rear_derailleur': 'Shimano Alivio, Shadow Design, SGS cage, 9-speed',
    'front_hub': 'Specialized front hub disc, sealed bearings, 15mm thru-axle, 32h',
    'rear_hub': 'Specialized, sealed cartridge bearings, 12x148mm thru-axle, 28h',
    'inner_tubes': 'Schrader, 40mm valve',
    'spokes': 'Stainless, 14g',
    'rims': '650b disc, double-wall alloy, pinned, 32h',
    'front_tire': 'Nimbus II Sport Reflect, 60 TPI, 650b x 2.3"',
    'rear_tire': 'Nimbus II Sport Reflect, 60 TPI, 650b x 2.3"',
    'saddle': 'Body Geometry "The Cup," 6-degree rise, elastomer base, steel rails, SWAT™ compatible mounts, 245mm',
    'seatpost': 'Specialized 2-bolt head, forged alloy, 8mm offset, micro-adjust, 30.9mm',
    'stem': 'Specialized Flowset, alloy, 20-degree w/ display mount, 31,8mm',
    'handlebars': 'Specialized, alloy, 30-degree backsweep, 26mm rise, 680mm width, 31.8mm',
    'grips': "Body Geometry Women's Contour",
    'front_brake': 'Tektro HD-T286, hydraulic disc, 180mm',
    'rear_brake': 'Tektro HD-T286, hydraulic disc, 160mm',
    'pedals': 'Specialized Commuter w/ grip tape & reflectors',
    'kickstand': 'Specialized kickstand, 40mm mount',
    'bell': 'Simple bell',
    'seat_binder': 'Alloy, bolt-type, 34.9mm',
    'fork': 'Turbo Como aluminum disc fork, 15x100mm thru-axle',
    'frame': 'Turbo Aluminum, low-entry frame, bottom bracket motor mount, Ground Control Geometry, fully integrated & lockable down tube battery, internal cable routing, fender/rack mounts, Smooth Welds',
    'ui_remote': 'Custom 2.2" computer. LCD display, USB plug, stem mount w/ custom handlebar remote',
    'battery': 'Specialized U1-460, On/Off button, state of charge display, 460Wh',
    'charger': 'Custom Specialized 42V2A Charger w/ Rosenberger plug, AC power cord included',
    'motor': 'Specialized 1.2, Custom Rx Trail-tuned motor, 250W Nominal',
    'wiring_harness': 'Custom Specialized wiring harness'
}
SWORKS_SPECS = {
    'chain': 'KMC X12 Ti, 12-speed',
    'crankset': 'Race Face Next SL, 170/175mm',
    'shift_levers': 'Shimano XTR M9100, 12-speed',
    'cassette': 'Shimano XTR M9100, 12-speed, 10-51t',
    'rear_derailleur': 'Shimano XTR M9100, 12-speed, Shadow Plus',
    'fork': 'FOX Factory Step-Cast 34, Fit4 damper, Kashima, Boost™, 44mm offset, 120mm of travel',
    'rear_shock': 'Custom RockShox Micro Brain shock w/ Spike Valve, AUTOSAG, 51x257mm',
    'saddle': 'Body Geometry Phenom Pro, carbon fiber rails, carbon fiber base, 143mm',
    'seat_binder': 'Alloy, 34.9mm, titanium bolt',
    'seatpost': 'FOX Factory Transfer, Kashima, Shimano Ispec-EV lever (S: 100mm, M-XL: 125mm)',
    'handlebars': 'S-Works Carbon Mini Rise, 6-degree upsweep, 8-degree backsweep, 10mm rise, 750mm, 31.8mm',
    'stem': 'S-Works SL',
    'grips': 'Specialized Sip grip, half-waffle, S/M: regular thickness, L/XL: XL thickness',
    'front_hub': 'Roval Control SL, sealed cartridge bearings, 15mm thru-axle, 110mm spacing, 24h',
    'rear_hub': 'Roval Control SL, DT Swiss Star Ratchet, 54t engagement, DT microspline, 12mm thru-axle, 148mm spacing, 28h',
    'inner_tubes': 'Presta, 60mm valve',
    'spokes': 'DT Swiss Industry',
    'rims': 'Roval Control SL, hookless carbon, 25mm internal width, tubeless-ready, hand-built',
    'front_tire': 'Ground Control, GRIPTON® compound, 60 TPI, 2Bliss Ready, 29x2.3"',
    'rear_tire': 'Fast Trak, GRID casing, GRIPTON® compound, 60 TPI, 2Bliss Ready, 29x2.3"',
    'front_brake': 'Shimano XTR Race M9100',
    'rear_brake': 'Shimano XTR Race M9100',
    'pedals': 'Specialized Dirt',
    'frame': 'S-Works FACT 12m, XC Geometry, Rider-First Engineered™, threaded BB, 12x148mm rear spacing, internal cable routing, 100mm of travel'
}


class SpecializedTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = Specialized(save_data_path=DATA_PATH)

    def test_get_prods_listings(self):
        bike_type = 'road'
        bike_cats = self._scraper._BIKE_CATEGORIES
        endpoint = bike_cats[bike_type]
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
                                      'specialized_prods_all.csv')
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
