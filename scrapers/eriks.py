"""
Module for scraping ericksbikeshop.com for its bike data.
"""
import math

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper
from scrapers.scraper_utils import DATA_PATH


class EriksBikes(Scraper):
    def __init__(self, save_data_path=DATA_PATH, page_size=60):
        super().__init__(base_url='https://www.eriksbikeshop.com',
                         source='eriks', save_data_path=save_data_path)
        self._page_size = page_size
        self._PROD_PAGE_ENDPOINT = '/eriks-bicycle-buying-guide.aspx'
        self._BIKE_CATEGORIES = self._get_categories()

    def _fetch_prod_listing_view(self, endpoint, page_size=60, page=1,
                                 guide=False):
        if guide:  # Get bikes guide page
            req_url = f'{self._BASE_URL}{endpoint}'
            return self._fetch_html(req_url)

        start_row = ((page - 1) * page_size) + 1
        req_url = f'{self._BASE_URL}{endpoint}?&startrow=' \
                  f'{start_row}&maxItems={page_size}'
        return self._fetch_html(req_url)

    # TODO: seems unnecessary, remove and embed directly into get_all_available_prods()
    def _get_max_num_prods(self, soup):
        """Raise error: Not implemented in this module."""
        raise NotImplemented

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()
        try:
            id_prod_specs = soup.find('div', attrs={'id': 'ProductSpecs'})
            table_specs = id_prod_specs.find('table',
                                             class_='seProductSpecTable')
            specs = table_specs.find_all('tr')

            # Get each spec_name, value pairing for bike product
            for spec in specs:
                name = spec.th.contents[0]
                value = spec.td.contents[0]
                spec_name = self._normalize_spec_fieldnames(name)
                prod_specs[spec_name] = value.strip()
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
            print(f'Getting {bike_type} bikes...')
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
            try:  # Handle no title year
                title_year = product_title.find(
                    'span', class_='seCleanTitleYear').contents[0]
            except AttributeError:
                title_year = ''
            product['description'] = item_name + title_year

            # Get brand name
            brand_name = product_title.find('span',
                                            class_='seBrandName').contents[0]
            product['brand'] = brand_name

            # Get price
            product_price = prod.find('div', class_='seProductPrice')
            reg_price = product_price.find('span', class_='seRegularPrice')

            if reg_price is None:
                price = product_price.find(
                    'span', class_='seSpecialPrice').contents[0]
                if price.find('-') > 0:
                    price = price.split('-')[0].strip()
                msrp = product_price.find(
                    'span', class_='seOriginalPrice').contents[0]
                if msrp.find('-') > 0:
                    msrp = msrp.split('-')[0].strip()
            else:
                try:
                    price = reg_price.contents[0]
                    if price.find('-') > 0:
                        price = price.split('-')[0].strip()
                    msrp = price
                except IndexError: # No price on page
                    # TODO: Get price from product specs page
                    price = '0'
                    msrp = '0'

            product['price'] = float(price.strip('$').replace(',', ''))
            product['msrp'] = float(msrp.strip('$').replace(',', ''))

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)
