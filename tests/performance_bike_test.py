# python modules
import unittest
from bs4 import BeautifulSoup

# package modules
from scrapers import PerformanceBikes


class PerformanceBikesTestCase(unittest.TestCase):
    def setUp(self):
        self.ps = PerformanceBikes(page_size=24)

    def test_update_facet_url(self):
        # case 1: initialize with default
        facet_str = '#facet:&productBeginIndex:0&facetLimit:&orderBy:5' \
                    '&pageView:list&minPrice:&maxPrice:&pageSize:72&'
        self.ps._update_facet_str(init=True)
        self.assertEqual(self.ps._facet, facet_str)

        # case 2: increment to next range
        self.ps._update_facet_str()
        self.assertNotEqual(self.ps._facet, facet_str)
        facet_str = '#facet:&productBeginIndex:71&facetLimit:&orderBy:5' \
                    '&pageView:list&minPrice:&maxPrice:&pageSize:72&'
        self.assertEqual(self.ps._facet, facet_str)

        # case 3: increment twice then check
        self.ps._update_facet_str()
        self.ps._update_facet_str()
        self.assertNotEqual(self.ps._facet, facet_str)
        facet_str = '#facet:&productBeginIndex:215&facetLimit:&orderBy:5' \
                    '&pageView:list&minPrice:&maxPrice:&pageSize:72&'
        self.assertEqual(self.ps._facet, facet_str)

    def test_get_bike_urls(self):
        response = self.ps.get_product_listings()
        self.assertEqual(False, response)

    def test_get_max_num_products(self):
        expected = 840  # from html file
        max_num = self.ps._get_max_num_prods(self.prod_list_soup)
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
        result = self.ps._get_prods_on_page(prod_list_soup)
        self.assertEqual(self.ps._page_size, len(result))
        for key in cases:
            self.assertTrue(key in result)
        for value in cases.values():
            self.assertTrue(value in result.values())

    def test_get_prod_listings(self):
        num_prods, result = self.ps.get_product_listings()
        self.assertTrue(num_prods, len(result))

    def test_get_prod_details(self):
        # load test prod details into memory
        with open('marin-hawk-hill-275-mountain-bike-2018-31-6715.html') as f:
            marin_prod_detail_text = f.read()

        with open('bkestrel-talon-105-le-road-bike-2018-31-8721.html') as f:
            bkestrel_prod_detail_text = f.read()

        marid_detail_soup = BeautifulSoup(marin_prod_detail_text, 'lxml')
        bkestrel_detail_soup = BeautifulSoup(bkestrel_prod_detail_text,
                                                  'lxml')
        pass


if __name__ == '__main__':
    unittest.main()
