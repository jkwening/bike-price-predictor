"""
Module for scraping giant.com for its bike data.
"""
import math
import json

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class Giant(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH):
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

    def _get_categories(self) -> dict:
        """Bike category endpoint encodings.

        Returns:
            categories: {bike_type: {subtypes: href}}
        """
        categories = dict()
        exclude = ['kids_bikes', 'view_all', 'electric_bikes']

        page = self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT)
        soup = BeautifulSoup(page, 'lxml')

        menu = soup.find('div', id='megamenubikes')
        container = menu.find('div', class_='row')
        cols = container.find_all('div', class_='col')

        for col in cols:
            title = col.h3.a.text.strip()
            title = self._normalize_spec_fieldnames(title)
            if title in exclude:
                continue
            subtypes = dict()
            a_tags = col.find('ul').find_all('a')
            for a_tag in a_tags:
                subtype = a_tag.string.strip()
                subtype = self._normalize_spec_fieldnames(subtype)
                if subtype in exclude:
                    continue
                subtypes[subtype] = a_tag['href']
            categories[title] = subtypes

        return categories

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available category
        bike_categories = self._get_categories()
        for bike_type, subtypes in bike_categories.items():
            for subtype, href in subtypes.items():
                print(f'Getting {bike_type}:{subtype}...')
                soup = BeautifulSoup(self._fetch_prod_listing_view(
                    endpoint=href), 'lxml')
                self._get_prods_on_current_listings_page(soup, bike_type,
                                                         subtype)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type, subtype):
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
                product = {
                    'site': self._SOURCE,
                    'bike_type': bike_type,
                    'subtype': subtype
                }

                a_tag = bike.a
                product['href'] = a_tag['href']
                product['brand'] = a_tag['data-product-brand']
                product['description'] = a_tag['data-product-name']
                prod_id = bike['id']
                product['product_id'] = prod_id

                # Parse price
                price = bike.find('span', class_='price').string
                price = float(price.strip().strip('$').replace(',', ''))
                product['price'] = price
                product['msrp'] = price
                self._products[prod_id] = product
                print(f'\t\t[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()

        # parse details/description
        details = ''
        div_intro = soup.find(id='intro')
        for string in div_intro.stripped_strings:
            details += string + '\n'
        prod_specs['details'] = details

        # parse tech specifications
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
