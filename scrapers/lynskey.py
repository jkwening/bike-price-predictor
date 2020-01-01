"""
Module for scraping lynskeyperformance.com for its bike data.
"""
from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class Lynskey(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH):
        super().__init__(base_url='https://lynskeyperformance.com',
                         source='lynskey',
                         save_data_path=save_data_path)
        self._CATEGORIES = {
            'road': '/road-bikes/',
            'gravel': '/road/gravel',
            'mountain': '/mountain-bikes/'
        }

    def _fetch_prod_listing_view(self, endpoint):
        req_url = f'{self._BASE_URL}{endpoint}'
        return self._fetch_html(req_url)

    def _get_max_num_prods(self, soup):
        """Get max num of products on current page."""
        raise NotImplementedError

    def _parse_prod_specs(self, soup) -> dict:
        """Returns list of dictionary representation of the product's specification."""
        prod_specs = dict()
        self._specs_fieldnames.add('frame_material')
        prod_specs['frame_material'] = 'titanium'

        try:
            div_specs = soup.find('div', class_='product-description')
            tables = div_specs.find_all('table')
            try:
                base_table = tables[2]
            except IndexError:  # Framesets don't have full specs
                print('Error: Not complete bike!')
                return prod_specs

            trs = base_table.find('tbody').find_all('tr')

            for tr in trs:
                tds = tr.find_all('td')
                spec = tds[0].text.strip()
                spec = self._normalize_spec_fieldnames(spec)
                self._specs_fieldnames.add(spec)
                value = tds[1].text.strip()
                prod_specs[spec] = value

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_specs

    @staticmethod
    def _get_next_page(soup):
        """Get next page URL if available.

        If page has 'next' button/a tag, then return True, 'URL' tuple. Where
        'URL' is link for the next page.

        Returns False, "" otherwise.
        """
        a_tag = soup.find('a', class_='next')

        if a_tag is None:
            return False, ''

        return True, a_tag['href']

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available category
        for bike_type, href in self._CATEGORIES.items():
            soup = BeautifulSoup(self._fetch_prod_listing_view(
                href), 'lxml')
            print(f'Parsing {bike_type}...')
            self._get_prods_on_current_listings_page(soup, bike_type)
            next_page, url = self._get_next_page(soup)

            # Iterate through all next pages
            while next_page:
                soup = BeautifulSoup(self._fetch_html(url), 'lxml')
                print(f'\t\tParsing next page...')
                self._get_prods_on_current_listings_page(soup, bike_type)
                next_page, url = self._get_next_page(soup)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type):
        """Parse products on page."""
        products = soup.find_all('article', class_='product-grid-item')

        for prod in products:
            product = dict()
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type
            product['brand'] = self._SOURCE

            # Get product details section and title
            div_details = prod.find('div', class_='product-grid-item-details')
            a_tag = div_details.find('h3', class_='product-item-title').a
            product['href'] = a_tag['href']
            title = a_tag['title']
            product['description'] = title.strip()

            # Parse prod id
            span_id = prod.find('span', class_='quick-shop-trigger')
            prod_id = span_id['data-quick-shop-trigger']
            product['product_id'] = prod_id

            # Parse price
            price = div_details.find('span', class_='price-value').string
            product['price'] = float(price.strip().strip('$').replace(',', ''))

            # Parse msrp accordingly
            try:
                was_price = div_details.find('span', class_='price-ns')
                msrp = was_price.find('span', class_='money').string
                product['msrp'] = float(
                    msrp.strip().strip('$').replace(',', ''))
            except AttributeError:  # handle not on sale
                product['msrp'] = product['price']

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)
