# python modules
import unittest
from bs4 import BeautifulSoup

# package modules
from scrapers import PerformanceBikes


class PerformanceBikesTestCase(unittest.TestCase):
    def setUp(self):
        self.pbs = PerformanceBikes(page_size=24)

    def test_update_facet_url(self):
        # case 1: initialize with default
        facet_str = '#facet:&productBeginIndex:0&facetLimit:&orderBy:5' \
                    '&pageView:list&minPrice:&maxPrice:&pageSize:72&'
        self.pbs._update_facet_str(init=True)
        self.assertEqual(self.pbs._facet, facet_str)

        # case 2: increment to next range
        self.pbs._update_facet_str()
        self.assertNotEqual(self.pbs._facet, facet_str)
        facet_str = '#facet:&productBeginIndex:71&facetLimit:&orderBy:5' \
                    '&pageView:list&minPrice:&maxPrice:&pageSize:72&'
        self.assertEqual(self.pbs._facet, facet_str)

        # case 3: increment twice then check
        self.pbs._update_facet_str()
        self.pbs._update_facet_str()
        self.assertNotEqual(self.pbs._facet, facet_str)
        facet_str = '#facet:&productBeginIndex:215&facetLimit:&orderBy:5' \
                    '&pageView:list&minPrice:&maxPrice:&pageSize:72&'
        self.assertEqual(self.pbs._facet, facet_str)

    def test_get_bike_urls(self):
        response = self.pbs.get_product_listings()
        self.assertEqual(False, response)

    def test_get_max_num_products(self):
        expected = 840  # from html file
        max_num = self.pbs._get_max_num_prods(self.prod_list_soup)
        self.assertEqual(expected, max_num)

    def test_get_prods_on_page(self):
        cases = {
            "/shop/bikes-frames/fuji-absolute-19-disc-flat-bar-road-bike-2018"
            "-31-8559": "Fuji Absolute 1.9 Disc Flat Bar Road Bike -2018",
            "/shop/bikes-frames/breezer-cloud-9-carbon-29er-mountain-bike"
            "-2018-31-8578": "Breezer Cloud 9 Carbon 29er Mountain Bike - 2018",
            "/shop/bikes-frames/marin-hawk-hill-275-mountain-bike-2018-31"
            "-6715": "Marin Hawk Hill 27.5 Mountain Bike - 2018",
            "/shop/bikes-frames/fuji-finest-10-le-womens-road-bike-2017-31"
            "-5619": "Fuji Finest 1.0 LE Women's Road Bike - 2017"
        }

        # load test html into memory
        with open('performance_bike_shop_bikes.html') as f:
            prod_list_text = f.read()

        prod_list_soup = BeautifulSoup(prod_list_text, 'lxml')
        result = self.pbs._get_prods_on_page(prod_list_soup)
        self.assertEqual(self.pbs._page_size, len(result))
        for key in cases:
            self.assertTrue(key in result)
        for value in cases.values():
            self.assertTrue(value in result.values())

    def test_get_prod_listings(self):
        num_prods, result = self.pbs.get_product_listings()
        self.assertTrue(num_prods, len(result))

    def test_get_prod_details(self):
        # example data
        marin_specs = {
            'Bottom Bracket': 'External seal cartridge bearing',
            'Brakes': 'Shimano BR-M315 hydraulic disc, 180mm/160mm rotor',
            'Cassette': 'Sunrace 10-speed, 11-42T',
            'Chain': 'KMC X10',
            'Crankset': 'Marin Forged Alloy 1x10, 32T, 76 BCD',
            'Fork': 'RockShox Recon Silver RL 27.5" fork, 120mm travel, '
                    'compression and rebound adjustment, alloy tapered steerer,'
                    ' 15mm thru axle',
            'Frame': 'Series 3 6061 aluminum frame, 27.5" wheels, 120mm travel '
                     'MultiTrac suspension, 135mm QR',
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

        # load test prod details into memory
        with open('marin-hawk-hill-275-mountain-bike-2018-31-6715.html') as f:
            marin_prod_detail_text = f.read()

        with open('bkestrel-talon-105-le-road-bike-2018-31-8721.html') as f:
            bkestrel_prod_detail_text = f.read()

        marin_detail_soup = BeautifulSoup(marin_prod_detail_text, 'lxml')
        bkestrel_detail_soup = BeautifulSoup(bkestrel_prod_detail_text,
                                                  'lxml')

        # case 1: exact match per example data
        result = self.pbs._parse_prod_specs(marin_detail_soup)
        self.assertEqual(len(marin_specs), len(result))
        for key in marin_specs.keys():
            self.assertEqual(marin_specs[key], result[key])

        # case 2: using second data, exact match in components
        result = self.pbs._parse_prod_specs(bkestrel_detail_soup)
        self.assertEqual(len(marin_specs), len(result))
        for key in marin_specs.keys():
            self.assertTrue(key in result.keys())


if __name__ == '__main__':
    unittest.main()
