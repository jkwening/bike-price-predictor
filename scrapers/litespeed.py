"""
Module for scraping litespeed.com for its bike data.
"""
from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class LiteSpeed(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH):
        super().__init__(base_url='https://litespeed.com',
                         source='litespeed',
                         save_data_path=save_data_path)
        self._CATEGORIES = {
            'road': '/collections/titanium-road-bikes',
            'gravel': '/collections/titanium-gravel-bikes',
            'mountain': '/collections/titanium-mountain-bikes'
        }

    def _fetch_prod_listing_view(self, endpoint):
        req_url = f'{self._BASE_URL}{endpoint}'
        return self._fetch_html(req_url)

    def _get_max_num_prods(self, soup):
        """Get max num of products on current page."""
        raise NotImplementedError

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

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type):
        """Parse products on page."""
        products = soup.find_all('a', class_='product-info__caption')

        for prod in products:
            product = dict()
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type
            product['brand'] = self._SOURCE
            product['href'] = prod['href']

            # Get product details section and title
            div_details = prod.find('div', class_='product-details')
            title = div_details.find('span', class_='title').string
            product['description'] = title.strip()

            # Generate prod id
            prod_id = self._normalize_spec_fieldnames(title)
            product['product_id'] = prod_id

            # Parse price
            price = div_details.find('span', class_='money').string.replace('USD', '')
            product['price'] = float(price.strip().strip('$').replace(',', ''))

            # Parse msrp accordingly
            try:
                was_price = div_details.find('span', class_='was_price')
                msrp = was_price.find('span', class_='money').string.replace('USD', '')
                product['msrp'] = float(
                    msrp.strip().strip('$').replace(',', ''))
            except AttributeError:  # handle not on sale
                product['msrp'] = product['price']

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup) -> list:
        """Returns list of dictionary representation of the product's specification."""
        prod_specs = list()
        self._specs_fieldnames.add('bike_sub_type')
        try:
            li_sect = soup.find('li', id='tab2')
            sub_name = ''
            sub_specs = dict()
            count = 0  # Track number of tables parsed for each section
            for child in li_sect.children:
                if child.name == 'h4':
                    sub_name = child.string.strip()
                    sub_specs = dict()
                    continue

                if child.name == 'div':
                    rows = child.find_all('tr')
                    for row in rows:
                        tds = row.find_all('td')
                        # Parse spec field names
                        spec = tds[0].text.strip()
                        spec = self._normalize_spec_fieldnames(spec)
                        # Parse spec value
                        value = tds[1].string
                        if value is None:
                            continue
                        sub_specs[spec] = value.strip()
                        self._specs_fieldnames.add(spec)

                    count += 1

                if count % 2 == 0 and count > 0:
                    sub_specs['bike_sub_type'] = sub_name  # sub-type as field name
                    prod_specs.append(sub_specs)
                    count = 0  # reset count

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_specs
