"""
Module for scraping canyon.com for its bike data.
"""
from bs4 import BeautifulSoup

from scrapers.scraper import Scraper
from scrapers.scraper_utils import DATA_PATH


class Canyon(Scraper):
    def __init__(self, save_data_path=DATA_PATH):
        super().__init__(base_url='https://www.canyon.com',
                         source='canyon', save_data_path=save_data_path)
        self._PROD_PAGE_ENDPOINT = '/en-us/'
        self._PAGE_SIZE = 72

    def _fetch_prod_listing_view(self, endpoint):
        req_url = f'{self._BASE_URL}{endpoint}'
        return self._fetch_html(req_url)

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()
        try:
            section = soup.find('section', class_='bike-detail-configuration')
            ul_specs = section.find('ul', class_='listing')

            for li in ul_specs.children:
                if li.name == 'li':
                    spec = li.text.strip().split('\n')[0]
                    spec = self._normalize_spec_fieldnames(spec)
                    value = li.find('span', class_='specs').string.strip().replace('  ', '')
                    value = value.replace('\n\n', ' ')
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
        exclude_list = ['bikes_on_stock', 'accessories',
                        'outlet', 'navigation']

        if soup is None:
            page = self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT)
            soup = BeautifulSoup(page, 'lxml')

        nav_cat = soup.find('nav', class_='navigation-shop')
        ul_cat = nav_cat.find('ul', class_='navigation')

        for li in ul_cat.children:
            if li.name == 'li':
                bike_cat = dict()
                try:
                    bike_cat['href'] = li.a['href']
                    title = li.a['data-nav'].strip().lower().replace(' ', '_')
                except KeyError:
                    continue
                if title in exclude_list:  # skip certain categories
                    continue

                # Get hrefs for bike models for this category
                models = list()
                for li_model in li.div.ul.li.ul.children:
                    if li_model.name == 'li':
                        models.append(li_model.a['href'])
                bike_cat['model_hrefs'] = models
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
            for href in bike_categories[bike_type]['model_hrefs']:
                print(f'Getting {href} for {bike_type} category...')
                # Get all available bikes
                endpoint = href + '#filter1=ALL'
                soup = BeautifulSoup(self._fetch_prod_listing_view(
                    endpoint), 'lxml')
                try:
                    self._get_prods_on_current_listings_page(soup, bike_type)
                except AttributeError:
                    print('\tError parsing', href)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type):
        """Parse products on page."""
        try:
            section = soup.find('section', id='bike_module')
            div_list = section.find('div', class_='bike-module-list')
            products = div_list.find_all('article', class_='product-box')
        except AttributeError:  # Alternative product tags
            section = soup.find('section', class_='teaser-section')
            products = section.find_all('article', class_='product-box')

        for prod in products:
            product = dict()
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type
            product['brand'] = self._SOURCE  # site is single brand
            product['href'] = prod.a['href'].replace(self._BASE_URL, '')

            # Generate custom product id
            title = prod.find('div', class_='product-title')
            product['description'] = title.text.strip().split('\n')[0]
            prod_id = product['description'].replace('.', '-').replace(' ', '-').lower()
            product['product_id'] = prod_id

            price = prod.find('p', class_='price-retail')
            price = price.find('span', class_='price').string
            product['price'] = float(
                price.strip().replace(',', '').split('$')[1])

            try:
                msrp = prod.find('p', class_='price-msr').span.string
                product['msrp'] = float(
                    msrp.strip().replace(',', '').split('$')[1])
            except AttributeError:  # handle not on sale
                product['msrp'] = product['price']

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _get_max_num_prods(self, soup):
        raise NotImplementedError
