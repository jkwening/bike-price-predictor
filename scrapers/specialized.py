"""
Module for scraping specialized.com for its bike data.
"""
import re
import json
from pprint import pprint

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class Specialized(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH):
        super().__init__(base_url='https://www.specialized.com',
                         source='specialized', save_data_path=save_data_path)
        self._page_size = 18  # 18 per page or all items
        self._EN_US_ENDPOINT = '/us/en'
        self._PROD_PAGE_ENDPOINT = '/us/en/shop/bikes/c/bikes'
        self._BIKE_CATEGORIES = {
            'mountain': '/us/en/shop/bikes/mountain-bikes/c/mountain',
            'road': '/us/en/shop/bikes/road-bikes/c/road',
            'fitness': '/us/en/shop/bikes/fitness--urban/c/active'
        }

    def _fetch_prod_listing_view(self, endpoint, show_all=True) -> dict:
        """Returns json dict object of products."""
        req_url = f'{self._BASE_URL}{endpoint}/plp'
        if show_all:  # Get all bikes page
            req_url += '?show=All'
        text = self._fetch_html(req_url)
        return json.loads(text)

    # TODO: seems unnecessary, remove and embed directly into get_all_available_prods()
    def _get_max_num_prods(self, soup):
        """Raise error: Not implemented in this module."""
        raise NotImplemented

    def _get_categories(self) -> dict:
        return self._BIKE_CATEGORIES

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available category
        for bike_type, href in self._BIKE_CATEGORIES.items():
            print(f'Getting {bike_type}...')
            data = self._fetch_prod_listing_view(endpoint=href)
            self._get_prods_on_current_listings_page(data, bike_type)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, data: dict, bike_type: str):
        """Parse products on page."""

        for result in data['results']:
            # skip framesets
            skip = False
            for facet_dict in result['facets']:
                if 'frameset' in facet_dict['name'].lower():
                    skip = True
                    break
            if skip:
                continue

            product = {
                'site': self._SOURCE,
                'bike_type': bike_type,
                'subtype': result.get('experience', bike_type)[0],
                'brand': self._SOURCE
            }
            # Get bike_type and prod_id
            prod_id = result['code']
            product['product_id'] = prod_id

            # Get page href and description
            product['href'] = result['url']
            product['description'] = result['name']

            # Get price
            product['msrp'] = float(
                result['formattedPrice'].strip('$').replace(',', ''))
            price = result['formattedDiscountPrice']
            if price is None:
                price = product['msrp']
            else:
                price = price.strip('$').replace(',', '')
            product['price'] = float(price)

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()
        # parse details/description
        tab1 = soup.find(id='tab1')
        details = tab1.text.strip()
        prod_specs['details'] = details

        # parse tech specifications
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
