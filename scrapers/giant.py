"""
Module for scraping giant.com for its bike data.
"""
import math
import json

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, DATA_PATH


class Giant(Scraper):
    def __init__(self, save_data_path=DATA_PATH):
        super().__init__(base_url='https://www.giant-bicycles.com',
                         source='giant', save_data_path=save_data_path)
        self._PROD_PAGE_ENDPOINT = '/us'

    def _fetch_prod_listing_view(self, endpoint):
        req_url = f'{self._BASE_URL}{endpoint}'
        return self._fetch_html(req_url)

    # TODO: seems unnecessary, remove and embed directly into get_all_available_prods()
    def _get_max_num_prods(self, soup):
        """Raise error: Not implemented in this module."""
        raise NotImplemented

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()
        div_specs = soup.find('div', id='specifications')
        try:
            tables = div_specs.find_all('table', class_='specifications')
        except AttributeError:
            return prod_specs
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

    def _get_categories(self) -> dict:
        """Bike category endpoint encodings.

        Returns:
            dictionary of dictionaries
        """
        categories = dict()

        page = self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT)
        soup = BeautifulSoup(page, 'lxml')

        menu = soup.find('div', id='megamenubikes')
        container = menu.find('div', class_='row')
        cols = container.find_all('div', class_='col')

        for col in cols:
            title = col.h3.a.text.strip()
            title = self._normalize_spec_fieldnames(title)
            href = col.h3.a['href']
            categories[title] = href

        return categories

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available category
        bike_categories = self._get_categories()
        for bike_type in bike_categories.keys():
            print(f'[get_all] Getting {bike_type}...')
            endpoint = bike_categories[bike_type]
            soup = BeautifulSoup(self._fetch_prod_listing_view(
                endpoint), 'lxml')
            self._get_prods_on_current_listings_page(soup, bike_type)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type):
        """Parse products on page."""
        div_prod_list = soup.find('div', id='productsContainer')
        tiles = div_prod_list.find_all('div', class_='tile')

        # Get model hrefs for products on page
        for tile in tiles:
            article = tile.find('article', class_='aos-item')
            href = article.a['href']
            print('\t[get_prods] Getting models for', href)

            # Get product info for each model available
            soup_model = BeautifulSoup(self._fetch_prod_listing_view(href), 'lxml')
            container = soup_model.find('div', id='productsContainer')
            bike_summary = container.find_all('div', class_='bike-summary')

            for bike in bike_summary:
                p_dict = dict()
                p_dict['site'] = self._SOURCE
                p_dict['bike_type'] = bike_type

                a_tag = bike.a
                p_dict['href'] = a_tag['href']
                p_dict['brand'] = a_tag['data-product-brand']
                p_dict['description'] = a_tag['data-product-name']
                prod_id = bike['id']
                p_dict['product_id'] = prod_id

                # Parse price
                price = bike.find('span', class_='price').string
                price = float(price.strip().strip('$').replace(',', ''))
                p_dict['price'] = price
                p_dict['msrp'] = price
                self._products[prod_id] = p_dict
                print(f'\t\t[{len(self._products)}] New bike: ', p_dict)
