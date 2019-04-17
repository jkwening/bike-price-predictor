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
        super().__init__(base_url='https://www.specialized.com',
                         source='specialized', save_data_path=save_data_path)
        self._page_size = 18  # 18 per page or all items
        self._PROD_PAGE_ENDPOINT = '/us/en/shop/bikes/c/bikes'
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
            div_table = soup.find('div', class_='product__specs-table')
            table_tr = div_table.find_all('tr', class_='product__specs-table-entry')

            for tr in table_tr:
                spec = tr.find('td', class_='product__specs-table-key').string.strip()
                spec = self._normalize_spec_fieldnames(spec)
                value = tr.find('td', class_='product__specs-table-value').string.strip()
                prod_specs[spec] = value
                self._specs_fieldnames.add(spec)

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_specs

    def _get_categories(self, soup=None) -> dict:
        """Bike category endpoint encodings.

        Returns:
            dictionary of dictionaries
        """
        categories = dict()

        if soup is None:
            page = self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT)
            soup = BeautifulSoup(page, 'lxml')

        nav_bar = soup.find('nav', attrs={'id': 'navigation'})
        bike_links = nav_bar.find('div', class_='BikesLink')
        cat_links = bike_links.find('li', class_='category-links')
        li_lvl2 = cat_links.find_all('li', class_='level2')

        for li in li_lvl2:
            bike_cat = dict()

            a_tag = li.div.a
            bike_cat['href'] = a_tag['href']
            title = self._normalize_spec_fieldnames(a_tag['title'])
            categories[title] = bike_cat
            # print(f'[{len(categories)}] New category {title}: ', bike_cat)

        return categories

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available category
        bike_categories = self._get_categories()
        for bike_type in bike_categories.keys():
            if bike_type == 'kids':  # skip kids bike page
                continue
            print(f'Getting {bike_type}...')
            endpoint = bike_categories[bike_type]['href']
            soup = BeautifulSoup(self._fetch_prod_listing_view(
                endpoint, show_all=True), 'lxml')
            self._get_prods_on_current_listings_page(soup, bike_type)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type):
        """Parse products on page."""
        div_prod_list = soup.find('div', class_='product-list')
        products = div_prod_list.find_all('div', class_='product-list__item')
        for prod in products:
            product = dict()
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type
            product['brand'] = 'specialized'  # site is single brand

            wrapper = prod.find('div', class_='product-list__item-wrapper')

            # Get bike_type and prod_id
            data_json = json.loads(wrapper['data-product-ic'])
            prod_id = data_json['id']
            product['product_id'] = prod_id

            # Get page href and description
            product['href'] = wrapper.a['href']
            product['description'] = wrapper.a['title']

            # Get price
            price, msrp = None, None  # initialize to None type
            try:
                div_price = wrapper.find('div', class_='product-list__item-price')
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
