"""
Module for scraping jensonusa.com for its bike data.
"""
from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class Jenson(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH, page_size=100):
        super().__init__(base_url='https://www.jensonusa.com',
                         source='jenson', save_data_path=save_data_path)
        self._page_size = page_size
        self._PROD_PAGE_ENDPOINT = '/Complete-Bikes'

    def _fetch_prod_listing_view(self, endpoint, page_size=None, page=None):
        req_url = f'{self._BASE_URL}{endpoint}'
        if page_size:
            req_url += f'?pn={page}&ps={page_size}'
        return self._fetch_html(req_url)

    def _get_max_num_prods(self, soup):
        """Raise error: Not implemented in this module."""
        raise NotImplemented

    def _get_categories(self):
        """Bike category endpoint encodings.

        Returns:
            dictionary of dictionaries
        """
        categories = dict()
        # categories that should be skipped
        exlude = ['jenson_usa_exclusive_builds', 'bikes_on_sale']
        page = self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT)
        soup = BeautifulSoup(page, 'lxml')

        div_cat = soup.find('div', class_='list-links')
        cats = div_cat.find_all('a')

        # Get all categories
        for a_tag in cats:
            bike_cat = dict()
            title = self._normalize_spec_fieldnames(a_tag.text)
            if title in exlude:
                continue
            bike_cat['href'] = a_tag['href'].replace(self._BASE_URL, '')
            categories[title] = bike_cat
            # print(f'[{len(categories)}] New category {title}: ', bike_cat)

        return categories

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Populate categories if missing
        categories = self._get_categories()

        # Scrape pages for each available category
        for bike_type in categories.keys():
            endpoint = categories[bike_type]['href']
            soup = BeautifulSoup(self._fetch_prod_listing_view(
                endpoint, page=0, page_size=self._page_size), 'lxml')
            print(f'Parsing {bike_type}...')
            self._get_prods_on_current_listings_page(soup, bike_type)
            try:
                pages = soup.find('span', class_='page-label').text
                pages = int(pages.strip().split()[-1])
            except AttributeError:
                # No next page
                pages = 0

            # Scrape all pages for bike category
            for page in range(1, pages):
                soup = BeautifulSoup(self._fetch_prod_listing_view(
                    endpoint, page=page, page_size=self._page_size), 'lxml')
                print(f'\t\tParsing next page...')
                self._get_prods_on_current_listings_page(soup, bike_type)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type):
        """Parse products on page."""
        try:
            section = soup.find('section', id='productList')
            container = section.find('div', class_='product-list-container')
            products = container.find_all('div', class_='item-content')
        except AttributeError:
            print('\tError: No products for', bike_type)
            return None

        for prod in products:
            product = dict()
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type

            # Parse prod id
            prod_id = prod['id']
            product['product_id'] = prod_id

            # Get page href, title, description, and brand
            a_tag = prod.find('a', class_='product-name')
            product['href'] = a_tag['href']
            product['description'] = a_tag.string.strip()
            product['brand'] = product['description'].split()[0]

            # Get price
            price = prod.find('div', class_='product-price-saleprice').text.strip()
            price = price.lower().replace('from', '').strip()
            product['price'] = float(price.strip('$').replace(',', ''))

            try:
                msrp = prod.find('div', class_='product-price-defprice').string.strip()
                msrp = msrp.replace('MSRP', '').strip()
                product['msrp'] = float(msrp.strip('$').replace(',', ''))
            except AttributeError:
                product['msrp'] = product['price']

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()
        try:
            id_prod_specs = soup.find('div', id='prod-tab-frame-D')
            table_specs = id_prod_specs.find_all('table', class_='spec')
            table_spec = table_specs[0]

            # Handle multiple table specs
            if len(table_specs) > 1:
                for table in table_specs:
                    caption = table.caption.string.lower().strip()
                    if caption == 'bike specifications':
                        table_spec = table
                        break

            # Get each spec_name, value pairing for bike product
            specs = table_spec.find_all('tr')
            for spec in specs:
                name = spec.th.string
                value = spec.td.text
                spec_name = self._normalize_spec_fieldnames(name)
                prod_specs[spec_name] = value.strip()
                self._specs_fieldnames.add(spec_name)

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')
        except IndexError:
            print('f\tError: Specifications table not available!')

        return prod_specs
