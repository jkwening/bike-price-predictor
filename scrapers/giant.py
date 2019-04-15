"""
Module for scraping giant.com for its bike data.
"""
import math
import json

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper
from scrapers.scraper_utils import DATA_PATH


class Giant(Scraper):
    def __init__(self, save_data_path=DATA_PATH):
        super().__init__(base_url='https://www.giant-bicycles.com',
                         source='giant', save_data_path=save_data_path)
        self._PROD_PAGE_ENDPOINT = '/us/bikes/startpage'

    def _fetch_prod_listing_view(self, endpoint):
        req_url = f'{self._BASE_URL}{endpoint}'

        # Spoof browser to avoid being flagged as an attack
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
            # 'Connection': 'keep-alive',
            # 'Cookie': 'corsActive=true; SPSI=9dfc4494d144ada004f48a02ede0fdcc; UTGv2=h4f7728ce06e8ec1da15a89311c1c3c87835; _ga=GA1.2.92630715.1555286400; _gid=GA1.2.30010004.1555286400; ai_user=6In3a|2019-04-14T23:59:59.757Z; Culture=us; tracker_device=16ee3852-7d53-4b67-8af7-551a393dceec; __distillery=fc2a100_5abf4553-62be-4357-a00f-fca8a3168e9c-59f4e479c-2dad24186f08-3d49; spcsrf=824b52752cfdd59851504ac8f5017a98; PRLST=bM; ai_session=VvSbi|1555296983756|1555300890354.465; adOtr=4AdQ94fd941'
        }
        return self._fetch_html(req_url, headers=headers)

    # TODO: seems unnecessary, remove and embed directly into get_all_available_prods()
    def _get_max_num_prods(self, soup):
        """Raise error: Not implemented in this module."""
        raise NotImplemented

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
        container = menu.find('div', class_='container')
        main_cats = container.find_all('div', class_='clearfix')

        for cat in main_cats:
            c_append = cat.h3.a.string.strip()
            c_append = self._normalize_spec_fieldnames(c_append)

            lis = cat.find_all('li')
            for li in lis:
                bike_cat = dict()
                bike_cat['href'] = li.a['href']
                title = li.a.string.strip()
                title = self._normalize_spec_fieldnames(title)
                if title == 'view_all':
                    continue
                title = f'{title}_{c_append}'
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
            print(f'[get_all] Getting {bike_type}...')
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
            print('\t[get_prods] Getting model products for', href)

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
                print(f'\t\t[{len(self._products)}] New bike: ', p_dict)
