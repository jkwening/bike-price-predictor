"""
Module for scraping foxvalley.com for its bike data.
"""
import math
import json

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper
from scrapers.scraper_utils import DATA_PATH


class FoxValley(Scraper):
    def __init__(self, save_data_path=DATA_PATH):
        super().__init__(base_url='http://www.giantfoxvalley.com',
                         source='foxvalley', save_data_path=save_data_path)
        self._page_size = 18  # 18 per page or all items
        self._PROD_PAGE_ENDPOINT = '/us/bikes/startpage'

    def _fetch_prod_listing_view(self, endpoint):
        req_url = f'{self._BASE_URL}{endpoint}'

        # Spoof browser to avoid 403 error code
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36'
        }
        return self._fetch_html(req_url, headers=headers)

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

        menu = soup.find('div', id='megamenubikes')
        ul_cat = menu.find('ul')
        a_tags = ul_cat.find_all('a')

        for a in a_tags:
            bike_cat = dict()
            bike_cat['href'] = a['href']
            title = a.string.strip()
            title = self._normalize_spec_fieldnames(title)
            categories[title] = bike_cat

        return categories

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available category
        bike_categories = self._get_categories()
        for bike_type in bike_categories.keys():
            print(f'Getting {bike_type}...')
            endpoint = bike_categories[bike_type]['href']
            soup = BeautifulSoup(self._fetch_prod_listing_view(
                endpoint), 'lxml')
            self._get_prods_on_current_listings_page(soup, bike_type)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type):
        """Parse products on page."""
        div_prod_list = soup.find('div', id='productsContainer')
        products = div_prod_list.find_all('div', class_='bikeseries-summary')
        for prod in products:
            product = dict()
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type

            product['href'] = prod.a['href']
            text_tag = prod.find('div', class_='text')
            brand_id = text_tag.find(
                'div', class_='store-brandlogo').img['class']

            if brand_id == 'brandid2':  # default brand is Giant
                product['brand'] = 'liv'
            else:
                product['brand'] = 'giant'

            # Get prod_id and description
            prod_id = prod['id']
            product['product_id'] = prod_id
            product['description'] = text_tag.h3.string.strip()

            # Get price
            price = prod['data-pricemin']
            product['price'] = float(
                price.strip().strip('$').replace(',', ''))
            msrp = prod['data-pricemax']
            product['msrp'] = float(
                msrp.strip().strip('$').replace(',', ''))

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)
