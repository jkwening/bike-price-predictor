"""
Module for scraping rei.com for its bike data.
"""
import os
import math
import json

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper
from scrapers.scraper_utils import DATA_PATH, TIMESTAMP
from scrapers.scraper_utils import get_bike_type_from_desc


class CityBikes(Scraper):
    def __init__(self, save_data_path=DATA_PATH, page_size=60):
        super().__init__(base_url='https://www.citybikes.com',
                         source='citybikes', save_data_path=save_data_path)
        self._page_size = page_size
        self._PROD_PAGE_ENDPOINT = 'product-list/bikes-1000/?'
        self._BIKE_CATEGORIES = self._get_categories()

    def _fetch_prod_listing_view(self, endpoint, page_size=60, page=1):
        start_row = ((page - 1) * page_size) + 1
        req_url = f'{self._BASE_URL}/{endpoint}&startrow=' \
                  f'{start_row}&maxItems={page_size}'
        return self._fetch_html(req_url)

    # TODO: seems unnecessary, remove and embed directly into get_all_available_prods()
    def _get_max_num_prods(self, soup):
        """Not used in this module."""
        return None

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()
        try:
            script_product_details = soup.find('script',
                                               attrs={
                                                   'data-client-store': 'product-details'})
            data = json.loads(script_product_details.string)
            specs = data['specs']

            # Get each spec_name, value pairing for bike product
            for spec in specs:
                name = spec['name']
                value = spec['values'][0]
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
            page = self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT)
            soup = BeautifulSoup(page, 'lxml')

        facet_cat = soup.find('div', attrs={'id': 'Facets-categories'})
        cats = facet_cat.find_all('li', class_='seFacet')

        # Get all categories
        for c in cats:
            bike_cat = dict()
            title = self._normalize_spec_fieldnames(c.a['title']).replace("'", "")
            bike_cat['href'] = c.a['href']
            bike_cat['filter_par'] = c.a['data-filterparameter']
            bike_cat['filter_val'] = int(c.a['data-filtervalue'])
            bike_cat['count'] = int(self._normalize_spec_fieldnames(
                c.span.contents[0]))
            categories[title] = bike_cat
            print(f'[{len(categories)}] New category {title}: ', bike_cat)

        return categories

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available category
        for bike_type in self._BIKE_CATEGORIES.keys():
            endpoint = self._BIKE_CATEGORIES[bike_type]['href']
            num_bikes = self._BIKE_CATEGORIES[bike_type]['count']
            pages = math.ceil(num_bikes / self._page_size)

            # Scrape all pages for bike category
            for page in range(pages):
                soup = BeautifulSoup(self._fetch_prod_listing_view(
                    endpoint, page=page + 1, page_size=self._page_size
                ), 'lxml')
                self._get_prods_on_current_listings_page(soup, bike_type)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type):
        """Parse products on page."""
        search_products = soup.find('div', attrs={'id': 'SearchProducts'})
        products = search_products.find_all('div', class_='seProduct')
        for prod in products:
            product = dict()
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type
            product_title = prod.find('div', class_='seProductTitle')

            # Get page href, product_id, and description
            href = product_title.a['href']
            product['href'] = href
            prod_id = href.split('-')[-2]
            product['product_id'] = prod_id
            item_name = product_title.find('span',
                                           class_='seItemName').contents[0]
            title_year = product_title.find(
                'span', class_='seCleanTitleYear').contents[0]
            product['description'] = item_name + title_year

            # Get brand name
            brand_name = product_title.find('span',
                                            class_='seBrandName').contents[0]
            product['brand'] = brand_name

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)
