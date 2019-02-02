import requests
import time
import os
from csv import DictWriter, DictReader
from datetime import datetime
import math
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

from scrapers.scraper_utils import create_directory_if_missing, MODULE_PATH
from scrapers.scraper_utils import DATA_PATH, TIMESTAMP


class Scraper(ABC):
    def __init__(self, base_url, source, save_data_path=DATA_PATH):
        self._BASE_URL = base_url
        self._SOURCE = source
        self._DATA_PATH = save_data_path
        self._TIMESTAMP = TIMESTAMP
        self._products = {}  # href, desc key,value pairs
        self._num_bikes = 0
        self._specs_fieldnames = set(['site'])
        self._bike_type = 'all'

    def _fetch_html(self, url, method='GET', params=None, data=None,
                    headers=None):
        """Fetch html page for bikes"""

        print(f'Performing {method} request for: {url}')
        response = requests.request(method=method, url=url, data=data,
                                    params=params, headers=headers)

        # check response status code
        if response.status_code != 200:
            raise FileNotFoundError(
                f'HTTPError - Status Code: {response.status_code}; Reason: '
                f'{response.reason}')

        return response.text

    @abstractmethod
    def _fetch_prod_listing_view(self, **kwargs):
        """Fetch product listing webpage for respective vendor."""
        pass

    @classmethod
    @abstractmethod
    def _get_max_num_prods(cls, soup):
        """
        Get the total number of produces available in page view.
        :param soup: beautiful soup to search through
        """
        # get div tag with class = 'title'
        div_product_listing_widget = soup.find('div',
                                               class_='productListingWidget')
        div_product = div_product_listing_widget.find('div',
                                                      class_='title')
        div_span = div_product.find('span')
        num_prods = div_span.string
        return int(num_prods.split()[-2])

    @abstractmethod
    def _get_prods_on_current_listings_page(self, **kwargs):
        """Get all bike products for the passed html page"""
        pass

    @abstractmethod
    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification.
        
        Note: fieldnames should be stored as lowercase strings.
        """
        pass

    def _write_prod_listings_to_csv(self) -> dict:
        """Save available bike products to csv file."""
        fname = f'{self._SOURCE}_prods_{self._bike_type}.csv'
        path = os.path.join(self._DATA_PATH, self._TIMESTAMP, fname)

        create_directory_if_missing(path)

        with open(file=path, mode='w', newline='', encoding='utf-8') as csvfile:
            prod_descs = list(self._products.keys())
            field_names = self._products[prod_descs[0]].keys()
            writer = DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()

            for desc in prod_descs:
                writer.writerow(self._products[desc])

        # return manifest row object of csv data
        return {
            'site': self._SOURCE, 'tablename': 'products',
            'bike_type': self._bike_type, 'filename': fname,
            'timestamp': self._TIMESTAMP, 'loaded': False,
            'date_loaded': None
        }

    def _write_prod_specs_to_csv(self, specs: dict,
                                 bike_type: str = '') -> dict:
        """Save bike product specifications to csv file."""
        if not bike_type:
            bike_type = self._bike_type

        fname = f'{self._SOURCE}_specs_{bike_type}.csv'
        path = os.path.join(self._DATA_PATH, self._TIMESTAMP, fname)

        create_directory_if_missing(path)

        with open(file=path, mode='w', newline='', encoding='utf-8') as csvfile:
            spec_descs = list(specs.keys())
            writer = DictWriter(csvfile, fieldnames=self._specs_fieldnames)
            writer.writeheader()

            for desc in spec_descs:
                writer.writerow(specs[desc])

        # return manifest row object of csv data
        return {
            'site': self._SOURCE, 'tablename': 'product_specs',
            'bike_type': self._bike_type, 'filename': fname,
            'timestamp': self._TIMESTAMP, 'loaded': False,
            'date_loaded': None
        }

    @abstractmethod
    def get_all_available_prods(self, to_csv=True) -> list:
        """Get all products currently available from site"""
        pass

    def get_product_specs(self, get_prods_from='site', bike_type: str = '',
                          to_csv=True) -> dict:
        """Get specifications for all available bikes on web site.
        
        Returns:
            manifest row data if written to csv, else specs dict object.
        """
        # determine how to get bike products
        if self._products and get_prods_from == 'memory':
            print('Have bike products listing in memory - PROCESSING...')
        elif get_prods_from == 'site':
            print('Getting bike products from site - SCRAPING SITE...')
            self.get_all_available_prods()
        elif get_prods_from:  # expecting file path of CSV file to load
            print(f'Loading products from {get_prods_from} - LOADING...')
            _, csv = get_prods_from.split('.')

            if csv != 'csv':
                raise TypeError('Not a CSV file type!')

            with open(file=get_prods_from, mode='r',
                      encoding='utf-8') as csv_file:
                products = dict()
                reader = DictReader(csv_file)

                for row in reader:
                    bike = dict(
                        row)  # TODO: isn't row already dict, seems unnecessary
                    products[bike['product_id']] = bike

            self._products = products
        else:
            raise ValueError('No products available!')

        start_timer = datetime.now()  # time how long to scrape all specs
        specs = dict()

        # iteratively get specifications page for each bike
        for bike in self._products:
            print(f'Fetching specifications for: {bike}')
            # define bike specifications url
            bike_href = self._products[bike]['href']
            bike_id = self._products[bike]['product_id']

            # Exception for url string
            if self._SOURCE == 'eriks':
                bike_url = bike_href
            else:
                bike_url = self._BASE_URL + bike_href

            # wait 1 second then get bike specification page
            time.sleep(0.10)
            try:
                bike_spec_soup = BeautifulSoup(self._fetch_html(url=bike_url),
                                               'lxml')
                specs[bike] = self._parse_prod_specs(bike_spec_soup)
            except FileNotFoundError:
                print(f'\tSpecifications page for {bike} not found!')
                specs[bike] = {}

            # ensure primary key fields are added
            specs[bike]['product_id'] = bike_id
            specs[bike]['site'] = self._SOURCE

        running_time = (datetime.now() - start_timer)
        print(f'Runtime for scraping specs: {running_time}')

        if to_csv:
            self._specs_fieldnames.add(
                'product_id')  # ensure id is field in specs file
            return self._write_prod_specs_to_csv(specs=specs,
                                                 bike_type=bike_type)

        return specs

    def _normalize_spec_fieldnames(self, fieldname: str) -> str:
        """Remove invalid chars and normalize as lowercase and no spaces."""
        fieldname = fieldname.strip()
        fieldname = fieldname.replace(' / ', '_')
        fieldname = fieldname.replace('-', '_')
        fieldname = fieldname.replace('(', '')
        fieldname = fieldname.replace(')', '')
        fieldname = fieldname.replace('[', '')
        fieldname = fieldname.replace(']', '')
        fieldname = fieldname.replace('{', '')
        fieldname = fieldname.replace('}', '')
        fieldname = fieldname.replace('/', '_')
        fieldname = fieldname.replace('.', '_')
        fieldname = fieldname.replace('&', '_')
        return fieldname.lower().replace(' ',
                                         '_')  # normalize: lowercase and no spaces
