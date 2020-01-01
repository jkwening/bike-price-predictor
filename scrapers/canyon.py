"""
Module for scraping canyon.com for its bike data.
"""
from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class Canyon(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH):
        super().__init__(base_url='https://www.canyon.com',
                         source='canyon', save_data_path=save_data_path)
        self._BIKE_MODELS_ENDPOINT = '/on/demandware.store/Sites-US-Site/en_US/Include-BikeFamilySlidersLazy?'
        self._PAGE_SIZE = 72
        self._BIKE_TYPES = ['mountain', 'road', 'urban', 'fitness']

    def _fetch_prod_listing_view(self, endpoint):
        req_url = f'{self._BASE_URL}{endpoint}'
        return self._fetch_html(req_url)

    def _get_bike_type_models_hrefs(self, bike_type):
        """Get list of model hrefs for bike type."""
        endpoint = self._BIKE_MODELS_ENDPOINT + 'mode=neutral&cgid=' + bike_type
        soup = BeautifulSoup(self._fetch_prod_listing_view(endpoint), 'lxml')
        a_tags = soup.find_all('a', class_='bikeModelSlider__allModels')
        hrefs = list()
        for tag in a_tags:
            hrefs.append(tag['href'])
        return hrefs

    def _get_categories(self) -> dict:
        """Fetch bike type categories and hrefs.

        Note: Canyon site has multiple bike type models hrefs.

        Returns:
            dictionary of dictionaries
        """
        categories = dict()
        for bike_type in self._BIKE_TYPES:
            hrefs = self._get_bike_type_models_hrefs(bike_type)
            categories[bike_type] = {'hrefs': hrefs}
        return categories

    def _get_prods_on_current_listings_page(self, soup, bike_type):
        """Parse products on page."""
        prod_grid = soup.find(id='section-product-grid')
        products = prod_grid.find_all('li', class_='productGrid__listItem')

        for prod in products:
            product = dict()
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type
            product['brand'] = self._SOURCE  # site is single brand

            # prod id
            div_scope = prod.find('div', class_='productTile')
            prod_id = div_scope['data-pid']
            product['product_id'] = prod_id

            # prod spec href
            a_tag = div_scope.find('a', class_='productTile__link')
            product['href'] = a_tag['href'].replace(self._BASE_URL, '')

            # other prod details
            desc = div_scope.find('span', class_='productTile__productName')
            text = desc.text.replace('New', '').strip()
            product['description'] = text

            price = div_scope.find('span', class_='productTile__productPriceSale').string
            product['price'] = float(
                price.strip().replace(',', '').split('$')[1])

            try:
                msrp = div_scope.find('span', class_='productTile__productPriceOriginal').string
                product['msrp'] = float(
                    msrp.strip().replace(',', '').split('$')[1])
            except AttributeError:  # handle not on sale
                product['msrp'] = product['price']

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _get_max_num_prods(self, soup):
        raise NotImplementedError

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available category
        categories = self._get_categories()
        for bike_type in categories.keys():
            for href in categories[bike_type]['hrefs']:
                print(f'Getting {href} for {bike_type} category...')
                soup = BeautifulSoup(self._fetch_prod_listing_view(
                    endpoint=href), 'lxml')
                try:
                    self._get_prods_on_current_listings_page(soup, bike_type)
                except AttributeError:
                    print('\tError parsing', href)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()
        try:
            comp_id = soup.find(id='all-components-section-panel')
            spec_li = comp_id.find_all('li', class_='allComponentsSpecItem')

            for li in spec_li:
                spec = li.find(class_='allComponentsSpecItem__title').string.strip()
                spec = self._normalize_spec_fieldnames(spec)

                # accumulate multiple values for specs
                value = ''
                values = li.find_all(class_='allComponentsSpecItem__listItem')
                for val in values:
                    value += '_' + val.string.strip()
                prod_specs[spec] = value.strip('_')
                self._specs_fieldnames.add(spec)

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_specs
