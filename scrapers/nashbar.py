import math

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class NashBar(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH):
        super().__init__(base_url='https://www.nashbar.com',
                         source='nashbar', save_data_path=save_data_path)
        self._BIKE_FRAMES_ENDPOINT = '/bikes-frames/c14941'

    def _fetch_prod_listing_view(self, endpoint, params=None):
        req_url = f'{self._BASE_URL}{endpoint}'
        return self._fetch_html(url=req_url, params=params)

    def _get_categories(self):
        """Bike category endpoint encodings.

        Returns:
            dictionary of dictionaries
        """
        categories = dict()
        page = self._fetch_prod_listing_view(endpoint=self._BIKE_FRAMES_ENDPOINT)
        soup = BeautifulSoup(page, 'lxml')

        main_content = soup.find('div', attrs={'id': 'maincontent'})
        category_page = main_content.find('div', attrs={'id': 'categorypage'})
        ul = category_page.find('ul', class_='category-menu-images')
        cats = ul.find_all('a')

        # Get all categories
        for c in cats:
            bike_cat = dict()
            title = self._normalize_spec_fieldnames(c['title']).replace("'", "")
            bike_cat['href'] = c['href']
            categories[title] = bike_cat

        return categories

    def _get_max_num_prods(self, soup):
        self._num_bikes = super()._get_max_num_prods(soup)

    def _get_prods_on_current_listings_page(self, soup, bike_type):
        """Get all bike products for the passed html page"""
        products_view = soup.find('div', attrs={'id': 'productsview'})
        items = products_view.find_all('div', class_='item')

        for item in items:
            product = dict()
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type

            # Get prod_id, prod_desc, and brand
            prod_id = item['data-id']
            product['product_id'] = prod_id
            product['description'] = item['data-name']
            product['brand'] = item['data-brand']

            # Get product's spec href
            div_detail = item.find('div', class_='detail')
            product['href'] = str(div_detail.a['href']).strip()

            # get current price and msrp (list_price)
            span_price = item.find('span', class_='productNormalPrice').string
            if span_price == 'See Price In Cart':
                price = 0.0
            else:
                price = float(span_price.strip().strip('$').replace(',', ''))
                product['price'] = price

            span_old_price = item.find('span', class_='productSpecialPrice')
            if span_old_price is None:
                product['msrp'] = price
            else:
                product['msrp'] = float(str(span_old_price.string).strip().split()[-1].strip('$').replace(',', ''))

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_spec = dict()

        try:
            div_spec = soup.find(id='tab-overview')
            div_std = div_spec.find('div', class_='std')

            if div_std:
                candidates = div_std.get_text()
            else:
                candidates = div_spec.get_text()

            # Identify where specifications begin and then split by ":"
            idx_spec = candidates.find('Specifications')
            if idx_spec == -1:
                idx_spec = candidates.find('Specs')
                str_replace = 'Specs'
            else:
                str_replace = 'Specifications'
            parse_str = candidates[idx_spec:]
            parse_str = parse_str.replace(str_replace, '').strip()
            split_specs = parse_str.split('\n')

            for spec in split_specs:
                try:
                    if not spec:
                        continue
                    name, value = spec.split(':')
                    name = self._normalize_spec_fieldnames(name)
                    prod_spec[name] = value.strip()
                    self._specs_fieldnames.add(name)
                except ValueError:
                    print(f'\tValue ErrorError: {spec}')
        except AttributeError as err:
            print(f'\tAttribute Error: {err}')

        print('Parsed product specs:', prod_spec)
        return prod_spec

    def get_all_available_prods(self, to_csv=True) -> list:
        """Get all products currently available from site"""
        # ensure product listings dictionary is empty
        self._products = {}
        self._num_bikes = 0

        # Get products for each bike category
        categories = self._get_categories()
        for bike_type in categories.keys():
            skip = ['bmx_bikes',
                    'bike_forks_mountain_suspension',
                    'bike_frame_protection', 'bike_frames',
                    'kids_bikes_balance_bikes']
            if bike_type in skip:
                continue
            endpoint = categories[bike_type]['href']

            # Calculate total number of pages
            html = self._fetch_prod_listing_view(endpoint)
            soup = BeautifulSoup(html, 'lxml')

            page_totals_view = soup.find('div', attrs={'id': 'pagetotalsview'})
            result = page_totals_view.string.split()
            num_pages = math.ceil(int(result[5]) / int(result[3]))

            self._get_prods_on_current_listings_page(soup, bike_type)

            # get remaining pages
            for p in range(2, num_pages + 1):
                html = self._fetch_prod_listing_view(endpoint, {'p': p})
                soup = BeautifulSoup(html, 'lxml')
                self._get_prods_on_current_listings_page(soup, bike_type)

            # Update num_bikes tracker
            self._num_bikes = len(self._products)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()
