"""
Module for scraping foxvalley.com for its bike data.
"""
import math
import json

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, DATA_PATH


class FoxValley(Scraper):
    def __init__(self, save_data_path=DATA_PATH):
        super().__init__(base_url='http://www.giantfoxvalley.com',
                         source='foxvalley', save_data_path=save_data_path)
        self._PROD_PAGE_ENDPOINT = '/us/bikes/startpage'

    def _fetch_prod_listing_view(self, endpoint):
        req_url = f'{self._BASE_URL}{endpoint}'
        return self._fetch_html(req_url)

    # TODO: seems unnecessary, remove and embed directly into get_all_available_prods()
    def _get_max_num_prods(self, soup):
        """Raise error: Not implemented in this module."""
        raise NotImplemented

    def _get_categories(self) -> dict:
        """Bike category endpoint encodings.

        Returns:
            dictionary of dictionaries
        """
        categories = dict()
        print('\nFetching categories data...')
        page = self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT)
        soup = BeautifulSoup(page, 'lxml')

        menu = soup.find('div', id='megamenubikes')
        a_tags = menu.find_all('ul li a')

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

        # Get model hrefs for products on page
        for prod in products:
            href = prod.a['href']
            print('[get_prods] Getting model products for', href)

            if len(self._products) == 20:
                print(href)

            # Get product info for each model available
            soup_model = BeautifulSoup(self._fetch_prod_listing_view(href), 'lxml')
            container = soup_model.find('div', id='productsContainer')
            bike_summary = container.find_all('div', class_='bike-summary')

            for bike in bike_summary:
                p_dict = dict()
                p_dict['site'] = self._SOURCE
                p_dict['bike_type'] = bike_type

                a_tag = bike.article.a
                p_dict['href'] = a_tag['href']
                p_dict['brand'] = a_tag['data-product-brand']
                p_dict['description'] = a_tag['data-product-name']
                prod_id = p_dict['description'].lower().replace(' ', '-')
                p_dict['prod_id'] = prod_id
                price = bike.find('span', class_='currentprice').string
                price = float(price.strip().strip('$').replace(',', ''))
                p_dict['price'] = price
                p_dict['msrp'] = price
                self._products[prod_id] = p_dict
                print(f'\t[{len(self._products)}] New bike: ', p_dict)

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()
        div_specs = soup.find('div', id='specifications')
        tables = div_specs.find_all('table', class_='specifications')
        trs = list()

        # Get all tr tags for both table tags
        for table in tables:
            trs += table.find_all('tr')

        try:
            for tr in trs:
                spec = tr.th.string.strip()
                spec = self._normalize_spec_fieldnames(spec)
                value = tr.td.string.strip()
                prod_specs[spec] = value
                self._specs_fieldnames.add(spec)

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_specs
