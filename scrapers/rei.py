"""
Module for scraping rei.com for its bike data.
"""
import json
import math

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper
from scrapers.scraper_utils import DATA_PATH


class Rei(Scraper):
    def __init__(self, save_data_path=DATA_PATH, page_size=90):
        self._page_size = page_size
        super().__init__(base_url='http://www.rei.com',
                         source='rei', save_data_path=save_data_path)
        self._BIKES_ENDPOINT = 'c/bikes'

    def _fetch_prod_listing_view(self, endpoint=None, bike='bikes',
                                 page=1, page_size=90):
        if endpoint is None:
            endpoint = 'search-ui/rest/search/products/results?'
            r = f'category%3A{bike}'
            origin = 'web'
            req_url = f'{self._BASE_URL}/{endpoint}r={r}&origin={origin}&page={page}&pagesize={page_size}'
        else:
            req_url = f'{self._BASE_URL}/{endpoint}'

        return self._fetch_html(req_url)

    def _get_categories(self):
        """Return bike category links from general bike page."""
        categories = dict()
        html = self._fetch_prod_listing_view(endpoint=self._BIKES_ENDPOINT)
        soup = BeautifulSoup(html, 'lxml')

        div_categories = soup.find(id='filter-Categories')
        a_tags = div_categories.find_all('a')

        for a in a_tags:
            cat = dict()
            cat['href'] = a['href']
            bike_type = a.text.strip().lower().split(':')[1]
            bike_type, count = bike_type.split('(')
            bike_type = bike_type.replace('bikes', '').strip()
            bike_type = self._normalize_spec_fieldnames(bike_type)
            count = int(count.strip(')').strip())
            cat['total'] = count
            categories[bike_type] = cat

        return categories

    # TODO: seems unnecessary, remove and embed directly into get_all_available_prods()
    def _get_max_num_prods(self, soup):
        """Get total number of products available."""
        data = json.loads(self._fetch_prod_listing_view(page_size=self._page_size))
        return int(data['query']['totalResults'])

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Get products for each bike type category
        categories = self._get_categories()
        for bike_type in categories.keys():
            bike = categories[bike_type]['href'].split('/')[-1]
            page_num = 1
            data = json.loads(
                self._fetch_prod_listing_view(
                    page_size=self._page_size, bike=bike
                )
            )

            num_pages = math.ceil(int(data['query']['totalResults']) / int(data['query']['upperResult']))

            # Scrape first page while its in memory then fetch and scrape the remaining pages
            self._get_prods_on_current_listings_page(data, bike_type)
            while True:
                page_num += 1
                if page_num > num_pages:
                    break
                else:
                    data = json.loads(self._fetch_prod_listing_view(
                        page=page_num, page_size=self._page_size, bike=bike)
                    )
                    self._get_prods_on_current_listings_page(data, bike_type)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, data, bike_type):
        results = data['results']

        for prod in results:
            product = {'site': 'rei', 'bike_type': bike_type}
            brand = prod['brand']
            title = prod['cleanTitle']
            product['brand'] = brand
            product['description'] = f'{brand} {title}'
            product['product_id'] = prod['prodId']
            product['href'] = prod['link']
            display_price = prod['displayPrice']
            product['price'] = display_price['max']
            product['msrp'] = display_price['compareAt']

            self._products[prod['prodId']] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup, garage=False):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()

        # Get correct scrip json per rei or rei-garage
        if garage:
            script = soup.find('script',
                               attrs={'id': 'page-data'})
            data = json.loads(script.string)
            specs = data['product']['specifications']['specs']
        else:
            script = soup.find('script',
                               attrs={'data-client-store': 'product-details'})
            data = json.loads(script.string)
            specs = data['specs']

        try:
            # Get each spec_name, value pairing for bike product
            for spec in specs:
                name = spec['name']
                value = spec['values'][0]
                spec_name = self._normalize_spec_fieldnames(name)
                prod_specs[spec_name] = value
                self._specs_fieldnames.add(spec_name)

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_specs
