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

    def _get_categories(self) -> dict:
        """Bike category endpoint encodings.

        Returns:
            dictionary of dictionaries
        """
        categories = dict()
        exclude = ['bmx_bikes', 'bike_forks_mountain_suspension', 'bike_frames',
                   'kids_bikes_balance_bikes', 'bike_frame_protection']
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
            if title in exclude:
                continue
            categories[title] = c['href']

        return categories

    def _get_subtypes(self) -> dict:
        bikes = dict()
        categories = self._get_categories()
        for bike_type, href in categories.items():
            subtypes = dict()
            soup = BeautifulSoup(self._fetch_prod_listing_view(endpoint=href),
                                 'lxml')
            filter_view = soup.find(id='filtersview')
            cat_names = filter_view.find_all('li', class_='categoryname')
            if not cat_names:  # remap to bike_type if no subtypes
                bikes[bike_type] = {bike_type: href}
                continue

            for cat in cat_names:
                subtype = cat.a['title']
                subtype = self._normalize_spec_fieldnames(subtype)
                subtypes[subtype] = cat.a['href']
            bikes[bike_type] = subtypes
        return bikes

    def _get_max_num_prods(self, soup):
        self._num_bikes = super()._get_max_num_prods(soup)

    def _get_prods_on_current_listings_page(self, soup, bike_type, subtype):
        """Get all bike products for the passed html page"""
        products_view = soup.find('div', attrs={'id': 'productsview'})
        items = products_view.find_all('div', class_='item')

        for item in items:
            product = {
                'site': self._SOURCE,
                'bike_type': bike_type,
                'subtype': subtype
            }

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
            text = div_spec.text.strip()

            # Identify where specifications begin and then split by ":"
            idx_spec = text.find('Specifications')
            if idx_spec == -1:
                idx_spec = text.find('Specs')
                str_replace = 'Specs'
            else:
                str_replace = 'Specifications'

            # store details
            details = text[:idx_spec].strip()
            prod_spec['details'] = details

            # process tech specifications
            parse_str = text[idx_spec:]
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
        categories = self._get_subtypes()
        for bike_type, subtypes in categories.items():
            for subtype, href in subtypes.items():
                # Calculate total number of pages
                html = self._fetch_prod_listing_view(endpoint=href)
                soup = BeautifulSoup(html, 'lxml')

                page_totals_view = soup.find('div', attrs={'id': 'pagetotalsview'})
                result = page_totals_view.string.split()
                num_pages = math.ceil(int(result[5]) / int(result[3]))

                self._get_prods_on_current_listings_page(soup, bike_type,
                                                         subtype)

                # get remaining pages
                for p in range(2, num_pages + 1):
                    html = self._fetch_prod_listing_view(
                        endpoint=href, params={'p': p}
                    )
                    soup = BeautifulSoup(html, 'lxml')
                    self._get_prods_on_current_listings_page(soup, bike_type,
                                                             subtype)

                # Update num_bikes tracker
                self._num_bikes = len(self._products)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()
