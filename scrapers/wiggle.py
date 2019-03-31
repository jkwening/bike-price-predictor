"""
Module for scraping wiggle.com for its bike data.

Notes:
- product listing requests uses get with query string params:
  - g: item number start position per items per page
  - _: 1543289729022 (default?) ??1543291456980 **not needed
  - ps: number of items per page - options: 24, 48, 96
returns html
- headers:
  - X-Requested-With: XMLHttpRequest
  - Referer: http://www.wiggle.com/cycle/bikes/?ps=96
    where '?ps' is # of items per page
- general bike search url: 'http://www.wiggle.com/cycle/bikes/'
  - returns all bike types

"""

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper
from scrapers.scraper_utils import DATA_PATH


class Wiggle(Scraper):
    def __init__(self, save_data_path=DATA_PATH, page_size=96):
        self._page_size = page_size
        self._BIKE_ENDPOINTS = {
            'road': 'road-bikes',
            'mountain': 'mountain-bikes',
            'cyclocross': 'cyclocross-bikes',
            'adventure': 'adventure-bikes',
            'touring': 'touring-bikes',
            'urban': 'urban-bikes',
            'track': 'track-bikes',
            'single-speed': 'single-speed-bikes',
            'time-trial': 'time-trial-bikes',
            'bmx': 'bmx-bikes',
            'kid': 'kids-bikes'
        }
        super().__init__(base_url='http://www.wiggle.com',
                         source='wiggle', save_data_path=save_data_path)

    def _fetch_prod_listing_view(self, prod_num=0, page_size=96):
        req_url = f'{self._BASE_URL}/cycle/bikes/?g={prod_num}&ps={page_size}'
        return self._fetch_html(req_url)

    def _get_max_num_prods(self, soup):
        """Get total number of products available."""
        text_block = soup.find('div', class_='bem-paginator__text-block').string

        if text_block:
            return int(text_block.split()[-1])

        return 0  # implies no products on page

    def _get_prods_on_current_listings_page(self, soup):
        div_id_products = soup.find('div', attrs={'id': 'search-results'})
        div_products_list = div_id_products.find_all('div',
                                                     class_='js-result-list-item')

        for prod_info in div_products_list:
            product = dict()
            product['site'] = self._SOURCE

            # get id
            prod_id = prod_info['data-id']
            product['product_id'] = prod_id

            # get page href, description, and parse brand
            prod_a = prod_info.a
            prod_href = prod_a['href'].split('/')[3]
            product['href'] = f'/{prod_href}'
            desc = prod_a['title']
            product['description'] = desc
            product['brand'] = desc.split()[0]

            # get current and msrp price
            try:  # handle possible "TEMPORARILY OUT OF STOCK" scenario
                prod_price = prod_info.find('span',
                                            class_='bem-product-price__unit--grid')
                price = prod_price.string.split('-')[-1]
                price = float(price.strip().strip('$').replace(',', ''))
                product['price'] = price

                prod_discount = prod_info.find('span',
                                               class_='bem-product_price__discount')

                if prod_discount:
                    discount = prod_discount.string.split('-')[-1]
                    discount = float(discount.strip().split()[-1].strip('%')) / 100.0
                    product['msrp'] = round(price / (1.0 - discount), 2)
                else:
                    product['msrp'] = price
            except AttributeError:
                print("TEMPORARILY OUT OF STOCK")
                product['price'] = -1
                product['msrp'] = -1

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()
        try:
            div_product_desc_table = soup.find('div',
                                               class_='bem-pdp__product-description--tabular')
            li_feature_items = div_product_desc_table.find_all('li',
                                                               class_='bem-pdp__features-item')

            # Get each spec_name, value pairing for bike product
            for feature in li_feature_items:
                try:
                    spec_name, spec_value = feature.string.split(': ')
                    spec_name = self._normalize_spec_fieldnames(spec_name)
                    prod_specs[spec_name] = spec_value.strip()
                    self._specs_fieldnames.add(spec_name)
                except ValueError as err:
                    continue

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_specs

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Get initial page and determine total number of products pages to scrape
        page_soup = BeautifulSoup(
            self._fetch_prod_listing_view(),
            'lxml')
        total_products = self._get_max_num_prods(soup=page_soup)

        # Scrape first page while its in memory then fetch and scrape the remaining pages
        self._get_prods_on_current_listings_page(soup=page_soup)
        self._num_bikes = len(self._products)
        print(f'Current number of products: {len(self._products)}')

        while self._num_bikes < total_products:
            page_soup = BeautifulSoup(
                self._fetch_prod_listing_view(prod_num=self._num_bikes + 1),
                'lxml')
            self._get_prods_on_current_listings_page(soup=page_soup)
            self._num_bikes = len(self._products)
            print(f'Current number of products: {self._num_bikes}')

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()
