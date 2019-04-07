import math
import time

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper
from scrapers.scraper_utils import DATA_PATH
from scrapers.scraper_utils import get_bike_type_from_desc

"""
base url = https://www.bikenashbar.com/cycling/bikes-frames#facet:&productBeginIndex:0&facetLimit:&orderBy:&pageView:grid&minPrice:&maxPrice:&pageSize:&

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


class NashBar(Scraper):
    def __init__(self, save_data_path=DATA_PATH):
        super().__init__(base_url='https://www.nashbar.com',
                         source='nashbar', save_data_path=save_data_path)
        self._BIKE_FRAMES_ENDPOINT = '/bikes-frames/c14941'
        self._BIKE_CATEGORIES = self._get_categories()

    def _fetch_prod_listing_view(self, endpoint, params=None):
        req_url = f'{self._BASE_URL}{endpoint}'
        return self._fetch_html(url=req_url, params=params)

    def _get_categories(self, soup=None):
        """Bike category endpoint encodings.

        Returns:
            dictionary of dictionaries
        """
        categories = dict()

        if soup is None:
            page = self._fetch_prod_listing_view(endpoint=self._BIKE_FRAMES_ENDPOINT)
            soup = BeautifulSoup(page, 'lxml')

        main_content = soup.find('div', attrs={'id': 'maincontent'})
        category_page = main_content.find('div', attrs={'id': 'categorypage'})
        ul = category_page.find('ul', class_='category-menu-images')
        cats = ul.find_all('a')

        # Get all categories
        for c in cats:
            bike_cat = dict()
            title = self._normalize_spec_fieldnames(c['title']).replace("'", "")
            bike_cat['href'] = c['href']
            categories[title] = bike_cat

        return categories

    def _get_max_num_prods(self, soup):
        self._num_bikes = super()._get_max_num_prods(soup)

    def _get_prods_on_current_listings_page(self, soup, bike_type):
        """Get all bike products for the passed html page"""
        products_view = soup.find('div', attrs={'id': 'productsview'})
        items = products_view.find_all('div', class_='item')

        for item in items:
            product = dict()
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type

            # Get prod_id, prod_desc, and brand
            prod_id = item['data-id']
            product['product_id'] = prod_id
            product['description'] = item['data-name']
            product['brand'] = item['data-brand']

            # Get product's spec href
            div_detail = item.find('div', class_='detail')
            product['href'] = str(div_detail.a['href']).strip()

            # get current price and msrp (list_price)
            span_price = item.find('span', class_='productNormalPrice').string
            if span_price == 'See Price In Cart':
                price = 0.0
            else:
                price = float(span_price.strip().strip('$').replace(',', ''))
                product['price'] = price

            span_old_price = item.find('span', class_='productSpecialPrice')
            if span_old_price is None:
                product['msrp'] = price
            else:
                product['msrp'] = float(str(span_old_price.string).strip().split()[-1].strip('$').replace(',', ''))

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_spec = dict()

        try:
            div_spec = soup.find(id='tab-overview')
            div_std = div_spec.find('div', class_='std')

            if div_std:
                candidates = div_std.get_text()
            else:
                candidates = div_spec.get_text()

            # Identify where specifications begin and then split by ":"
            idx_spec = candidates.find('Specifications')
            if idx_spec == -1:
                idx_spec = candidates.find('Specs')
                str_replace = 'Specs'
            else:
                str_replace = 'Specifications'
            parse_str = candidates[idx_spec:]
            parse_str = parse_str.replace(str_replace, '').strip()
            split_specs = parse_str.split('\n')

            for spec in split_specs:
                try:
                    if not spec:
                        continue
                    name, value = spec.split(':')
                    name = self._normalize_spec_fieldnames(name)
                    prod_spec[name] = value.strip()
                    self._specs_fieldnames.add(name)
                except ValueError:
                    print(f'\tValue ErrorError: {spec}')
        except AttributeError as err:
            print(f'\tAttribute Error: {err}')

        print('Parsed product specs:', prod_spec)
        return prod_spec

    def get_all_available_prods(self, to_csv=True) -> list:
        """Get all products currently available from site"""
        # ensure product listings dictionary is empty
        self._products = {}
        self._num_bikes = 0

        # Get products for each bike category
        for cat in self._BIKE_CATEGORIES:
            skip = ['bmx_bikes',
                    'bike_forks_mountain_suspension',
                    'bike_frame_protection', 'bike_frames',
                    'kids_bikes_balance_bikes']
            if cat in skip:
                continue
            bike_type = cat
            endpoint = self._BIKE_CATEGORIES[cat]['href']

            # Calculate total number of pages
            html = self._fetch_prod_listing_view(endpoint)
            soup = BeautifulSoup(html, 'lxml')

            page_totals_view = soup.find('div', attrs={'id': 'pagetotalsview'})
            result = page_totals_view.string.split()
            num_pages = math.ceil(int(result[5]) / int(result[3]))

            self._get_prods_on_current_listings_page(soup, bike_type)

            # get remaining pages
            for p in range(2, num_pages + 1):
                html = self._fetch_prod_listing_view(endpoint, {'p': p})
                soup = BeautifulSoup(html, 'lxml')
                self._get_prods_on_current_listings_page(soup, bike_type)

            # Update num_bikes tracker
            self._num_bikes = len(self._products)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()
