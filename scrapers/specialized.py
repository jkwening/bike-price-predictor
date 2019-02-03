"""
Module for scraping specialized.com for its bike data.
"""
import math
import json

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper
from scrapers.scraper_utils import DATA_PATH


class Specialized(Scraper):
    def __init__(self, save_data_path=DATA_PATH):
        super().__init__(base_url='https://www.specialized.com/us/en/',
                         source='specialized', save_data_path=save_data_path)
        self._page_size = 18  # 18 per page or all items
        self._PROD_PAGE_ENDPOINT = '/shop/bikes/c/bikes'
        # self._BIKE_CATEGORIES = self._get_categories()

    def _fetch_prod_listing_view(self, endpoint, page=1,
                                 show_all=False):
        if show_all:  # Get all bikes page
            req_url = f'{self._BASE_URL}{endpoint}?show=All'
        else:  # Get paginated page at specified page #
            req_url = f'{self._BASE_URL}{endpoint}?page={page}'
        return self._fetch_html(req_url)

    # TODO: seems unnecessary, remove and embed directly into get_all_available_prods()
    def _get_max_num_prods(self, soup):
        """Raise error: Not implemented in this module."""
        raise NotImplemented

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()
        try:
            # div_feat = soup.find('div', class_='feat')
            gspecs_div = soup.find('div', class_='specs')
            table_specs = gspecs_div.find('table')
            specs = table_specs.find_all('tr')

            # Get each spec_name, value pairing for bike product
            for spec in specs:
                name = ''
                for str in spec.th.stripped_strings:
                    name += str
                value = ''
                for str in spec.td.stripped_strings:
                    value += str
                spec_name = self._normalize_spec_fieldnames(name)
                prod_specs[spec_name] = value
                self._specs_fieldnames.add(spec_name)

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_specs

    def _get_categories(self, soup=None):
        """Bike category endpoint encodings.

        Returns:
            dictionary of dictionaries
        """
        categories = dict()

        if soup is None:
            page = self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT,
                                                 guide=True)
            soup = BeautifulSoup(page, 'lxml')

        bucket_cont = soup.find('div', class_='GBucketCont')
        cats = bucket_cont.find_all('div', class_='GBucket')

        # Get all categories
        for c in cats:
            bike_cat = dict()
            h2 = c.h2.contents[0].replace('& ', '')
            title = self._normalize_spec_fieldnames(h2)

            # Get href link
            bucket_links = c.find('div', class_='GBucketLinks')
            span = bucket_links.find('span')
            bike_cat['href'] = span.a['href']
            categories[title] = bike_cat
            # print(f'[{len(categories)}] New category {title}: ', bike_cat)

        return categories

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available category
        for bike_type in self._BIKE_CATEGORIES.keys():
            print(f'Getting {bike_type}...')
            endpoint = self._BIKE_CATEGORIES[bike_type]['href']

            # Scrape first page, get num bikes, and determine num pages
            soup = BeautifulSoup(self._fetch_prod_listing_view(
                endpoint, page=1), 'lxml')
            num_bikes = self._get_prods_on_current_listings_page(
                soup, bike_type, get_num_bikes=True
            )
            pages = math.ceil(num_bikes / self._page_size)

            # Scrape remaining pages for bike category
            for page in range(1, pages):
                soup = BeautifulSoup(self._fetch_prod_listing_view(
                    endpoint, page=page + 1), 'lxml')
                self._get_prods_on_current_listings_page(soup, bike_type)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup):
        """Parse products on page."""
        div_prod_list =soup.find('div', class_='product-list')
        products = div_prod_list.find_all('div', class_='product-list__item')
        for prod in products:
            product = dict()
            product['site'] = self._SOURCE
            product['brand'] = 'specialized' # site is single brand

            wrapper = prod.find('div', class_='product-list__item-wrapper')

            # Get bike_type and prod_id
            data_json = json.loads(wrapper['data-product-ic'])
            prod_id = data_json['id']
            product['product_id'] = prod_id
            bike_type = self._normalize_spec_fieldnames(
                data_json['p_subCategory1']
            )
            product['bike_type'] = bike_type

            # Get page href and description
            product['href'] = wrapper.a['href']
            product['description'] = wrapper.a['title']

            # Get price
            try:
                div_price = wrapper.find('div', class_='product-list__item-price')
                price, msrp = None, None  # initialize to None type
                price = div_price.find('span', class_='js-plp-price').string
                product['price'] = float(
                    price.strip().strip('$').replace(',', ''))
                msrp = div_price.find('span', class_='js-plp-price-old').string
                product['msrp'] = float(
                    msrp.strip().strip('$').replace(',', ''))
            except NameError:
                if price is None:
                    print(f'{prod_id}: No price available, setting to $0.00')
                    product['price'] = 0.0

                if msrp is None:
                    product['msrp'] = product['price']

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)
