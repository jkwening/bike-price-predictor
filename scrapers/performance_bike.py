import requests
import time
from bs4 import BeautifulSoup

SHOP_BIKES_BASE_URL = "https://www.performancebike.com/shop/bikes-frames"
FACET_MOD1_IDX = '#facet:&productBeginIndex:'
FACET_MOD2_VIEW = '&facetLimit:&orderBy:5&pageView:'
FACET_MOD3_SIZE = '&minPrice:&maxPrice:&pageSize:'
FACET_MOD4_END = '&'

"""
base url = https://www.performancebike.com/shop/bikes-frames#facet:&productBeginIndex:0&facetLimit:&orderBy:5&pageView:grid&minPrice:&maxPrice:&pageSize:&

- pageSize: can be 24, 48, 72 items per page
- pageView: can be 'grid' or 'list'**

### products tags
div class'productListingWidget' - main div for product
div class='product_listing_container' - houses products unordered list
ul class='grid_mode ?' - ul for grid type ? = grid/list
li - lists of products
div class='product' - div container for each product following li tag
div class='product_info' - house product related info tags
div class='product_name' - has a tag which includes href and product name
a ... href='...url_for_product'>...product_name_with_year</a>

div class='title>Products:< - start of getting number products displayed
span class='num_products'>($nbsp; # - # of # $nbsp;)< - range
"""


class PerformanceBikes(object):
    def __init__(self, page_size=72, page_view='list', ):
        self._page_size = page_size
        self._page_view = page_view
        self._product_begin_index = 0
        self._facet = ''
        self._update_facet_str(init=True)
        self._page_count = 1
        self._products = {}  # href, desc key,value pairs

    def _update_facet_str(self, init=False):
        """Updates facet query string with next index range"""
        if not init:
            self._product_begin_index =\
                (self._page_size * self._page_count) - 1
            self._page_count += 1

        self._facet = f'{FACET_MOD1_IDX}{self._product_begin_index}' \
                      f'{FACET_MOD2_VIEW}{self._page_view}{FACET_MOD3_SIZE}' \
                      f'{self._page_size}{FACET_MOD4_END}'

    def _fetch_html(self):
        """Fetch html page for bikes"""
        response = requests.get(SHOP_BIKES_BASE_URL + self._facet)

        # check response status code
        if response.status_code != 200:
            print(f'Error - Status Code: {response.status_code}; Reason: '
                  f'{response.reason}')
            raise Exception(f'HTTPError')

        return response.text

    def _get_max_num_prods(self, soup):
        """
        Get the total number of produces available in page view.
        :param soup: beautiful soup to search through
        :return: the max number of products
        """
        # get div tag with class = 'title'
        div_product_listing_widget = soup.find('div',
                                               class_='productListingWidget')
        div_product = div_product_listing_widget.find('div',
                                                      class_='title')
        div_span = div_product.find('span')
        num_prods = div_span.string
        return int(num_prods.split()[-2])

    def _get_prods_on_page(self, soup):
        """Get all bike products for the passed html page"""
        div_product_listing_widget = soup.find('div',
                                               class_='productListingWidget')
        div_product_name = div_product_listing_widget.find_all('div',
                                                        class_='product_name')
        for name in div_product_name:
            self._products[name.a['href']] = name.a.string
        return self._products

    def _prod_listings_to_csv(self):
        pass

    def _prod_details_to_csv(self):
        pass

    def get_product_listings(self):
        """Get all products currently available from site"""
        # refresh product listings dictionary if not empty
        if self._products:
            self._products = {}

        page_soup = BeautifulSoup(self._fetch_html(), 'lxml')
        num_prods = self._get_max_num_prods(soup=page_soup)
        num_pages = int(num_prods / self._page_size)

        # iterate through all grid pages
        for _ in range(num_pages):
            print(_)
            self._get_prods_on_page(soup=page_soup)
            self._update_facet_str(init=False)

            # wait 1 second then request next page
            time.sleep(1)
            page_soup = BeautifulSoup(self._fetch_html(), 'lxml')

        return num_prods, self._products

    def get_product_details(self, prod_name, prod_href):
        """Get bike details for given bike"""
        return None
